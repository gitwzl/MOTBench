import re
import os
import sys
import json
import warnings
import openpyxl
from collections import defaultdict
from norm import norm_en, norm_zh, norm_digit, units

warnings.filterwarnings('ignore')

# 配置参数
score_by_rule = True  # 指定打分方法，True为规则打分，False为LLM打分
lang = "en"  # 指定语言 "en" 或 "zh"
vllm_ocr_result_jsonfile = "ocr_en.json"  # ocr预测结果文件

# llm打分需要加载llm相关文件
if not score_by_rule:
    from libtool.llm import llm_judge_ocr

# ocr结果存放格式
# ["{category}/{imagename1}": "{ocr_result1}",
# ...,
# "{category}/{imagenamek}": "{ocr_resultk}"]

# 加载ocr结果
with open(vllm_ocr_result_jsonfile, "r", encoding="utf-8") as fr:
    preds = json.load(fr)

# 人工标注结果
if lang == "en":
    ref_ocr_result_excelfile = "data/text/English_menu.xlsx"
else:
    ref_ocr_result_excelfile = "data/text/Chinese_menu.xlsx"
workbook = openpyxl.load_workbook(ref_ocr_result_excelfile)
sheet = workbook.active

score_dict = defaultdict(list)
for row in sheet.iter_rows(min_row=3):
    number = row[0].value  # 序号
    if number is None:
        break

    category = row[1].value  # 类别
    imagename = row[2].value  # 图片名称

    vllm_ocr_result = preds[f"{category}/{imagename}"]  # 当前ocr预测结果

    dish = row[9].value  # 菜品

    if lang == "en":
        price = row[11].value  # 总价格
        unit = row[12].value
        item1 = row[13].value
        price1 = row[14].value
        item2 = row[15].value
        price2 = row[16].value
        item3 = row[17].value
        price3 = row[18].value
        item4 = row[19].value
        price4 = row[20].value
        item5 = row[21].value
        price5 = row[22].value
        all_items = [price, unit, price1, item1, price2, item2, price3, item3, price4, item4, price5, item5]
    else:
        price = row[12].value  # 总价格
        unit1 = row[13].value
        unit2 = row[14].value
        item1 = row[15].value
        price1 = row[16].value
        item2 = row[17].value
        price2 = row[18].value
        all_items = [price, unit1, unit2, price1, item1, price2, item2]

    # 文本归一化
    all_items = [norm_digit(item, lang) for item in all_items if item is not None]
    if lang == "en":
        dish = norm_en(dish)
        vllm_ocr_result = norm_en(vllm_ocr_result)
    else:
        dish = norm_zh(dish)
        vllm_ocr_result = norm_zh(vllm_ocr_result)

    # 逐行判断是否匹配
    find_lines = []
    for vllm_ocr_result_line in vllm_ocr_result.split("\n"):
        # LLM打分
        if not score_by_rule:
            score = llm_judge_ocr(dish, vllm_ocr_result)
        # 规则打分
        else:
            score = 1
            if dish not in vllm_ocr_result:
                score = 0

        if score == 1:
            find_lines.append(vllm_ocr_result_line)

    score = 0
    if len(find_lines) > 0:
        flags = []
        for find_line in find_lines:
            flag = "ok"

            # 有价格，漏识别
            if price and "not listed with price" in find_line:
                flag = "bad"

            # 没有单位，多识别出单位
            for u in units[lang]:
                if u in find_line and u not in " ".join(all_items):
                    flag = "bad"
                    break

            # 子项漏识别
            for item in all_items:
                if item and item not in find_line:
                    flag = "bad"
                    break

            flags.append(flag)

        if "ok" in flags:
            score = 1

    score_dict[category].append(score)

# 计算各类型图片OCR准确率
total_correct = 0
total_dish = 0
for category, score_list in score_dict.items():
    total_correct += score_list.count(1)
    total_dish += len(score_list)
    print(category, round(score_list.count(1) / len(score_list) * 100, 2))
print("all category", round(total_correct / total_dish * 100, 2))

import re
import os
import sys
import json
import warnings
from opwnpyxl.workbook import Workbook
from collections import defaultdict
from llm import llm_judge
from norm import norm_en, norm_zh

warnings.filterwarnings('ignore')

# 配置参数
score_by_rule = True # 指定打分方法，True为规则打分，False为LLM打分
lang = "en" # 指定语言 "en" 或 "zh"

# ocr预测结果
vllm_ocr_result_jsonfile = sys.argv[1]
with open(vllm_ocr_result_jsonfile, "r", encoding="utf-8") as fr:
    preds = json.load(fr)

# 人工标注结果
if lang == "en":
    ref_ocr_result_excelfile = "English_menu_ocr_ref.xlsx"
else:
    ref_ocr_result_excelfile = "Chinese_menu_ocr_ref.xlsx"
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

    dish = row[8].value  # 菜品

    # 文本归一化
    if lang == "en":
       dish = norm_en(dish)
       vllm_ocr_result = norm_en(vllm_ocr_result)
    else:
        dish = norm_zh(dish)
        vllm_ocr_result = norm_zh(vllm_ocr_result)

    # LLM打分
    if not score_by_rule:
        score = llm_judge(dish, vllm_ocr_result)
    # 规则打分
    else:
        score = 1
        if dish not in vllm_ocr_result:
            score = 0

    score_dict[category].append(score)

# 计算各类型图片OCR准确率
total_correct = 0
total_dish = 0
for category, score_list in score_dict.items():
    total_correct += score_list.count(1)
    total_dish += len(score_list)
    print(category, round(score_list.count(1) / len(score_list) * 100, 2))
print("all category", round(total_correct / total_dish * 100, 2))

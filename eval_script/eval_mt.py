import re
import os
import sys
import json
import warnings
from opwnpyxl.workbook import Workbook
from collections import defaultdict
from llm import llm_judge
from norm import norm_en, norm_zh, norm_digit, units
from cal_bleu_comet import cal_metric
from numpy import mean

warnings.filterwarnings('ignore')

# 配置参数
lang = "en"  # 指定语言 "en" 或 "zh"

# mt结果
vllm_mt_result_jsonfile = sys.argv[1]
with open(vllm_mt_result_jsonfile, "r", encoding="utf-8") as fr:
    preds = json.load(fr)

# 人工标注结果
if lang == "en":
    ref_ocr_result_excelfile = "English_menu_mt_ref.xlsx"
else:
    ref_ocr_result_excelfile = "Chinese_menu_mt_ref.xlsx"
workbook = openpyxl.load_workbook(ref_ocr_result_excelfile)
sheet = workbook.active

bleu_dict = defaultdict(list)
comet_dict = defaultdict(list)
for row in sheet.iter_rows(min_row=3):
    number = row[0].value  # 序号
    if number is None:
        break

    category = row[1].value  # 类别
    imagename = row[2].value  # 图片名称

    vllm_mt_result = preds[f"{category}/{imagename}"]  # 当前mt结果

    dish = row[8].value  # 菜品
    ref_dish = row[26].value  # 参考翻译菜品

    # 文本归一化
    if lang == "en":
        dish = norm_en(dish)
        vllm_mt_result = norm_en(vllm_mt_result)
    else:
        dish = norm_zh(dish)
        vllm_mt_result = norm_zh(vllm_mt_result)

    # 逐行判断是否匹配
    find_lines = []
    for vllm_ocr_result_line in vllm_mt_result.split("\n"):
        if dish in vllm_ocr_result_line:
            find_lines.append(vllm_ocr_result_line)

    mt = ""
    if len(find_lines) > 0:
        flags = []
        for find_line in find_lines:
            if ref_dish in find_line:
                mt = ref_dish
                break

            mt = llm_extra_mt(dish, find_line, lang)
            if len(mt) > 0:
                break

    bleu, comet = cal_metric(dish, mt, ref_dish, lang)
    bleu_dict[category].append(bleu)
    comet_dict[category].append(comet)

# 计算各类型图片BLEU指标
bleus = []
for category, score_list in bleu_dict.items():
    bleus.extend(score_list)
    print(category, "bleu", round(float(mean(score_list)), 2))
print("all category bleu", round(float(mean(bleus)), 2))

# 计算各类型图片COEMT指标
comets = []
for category, score_list in comet_dict.items():
    comets.extend(score_list)
    print(category, "comet", round(float(mean(score_list)), 2))
print("all category comet", round(float(mean(comets)), 2))

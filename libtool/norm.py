import re
from opencc import OpenCC

cc = OpenCC("t2s")
units = {"en": ["$", "￥", "yuan", "rp", "cny", "¥", "€", "£", "HKD", "₹", "₩", "₫", "₽"],
         "zh": ["份", "瓶", "杯", "桶", "斤", "扎", "罐", "串", "盒",
                "人", "根", "块", "支", "只", "个", "例", "片",
                "500g", "锅", "听", "碗", "位", "条", "套", "元", "$", "￥", "¥"]}


def norm_en(text):
    text = str(text).lower().strip()
    text = text.replace(" / ", "/").replace("‘", "'")
    text = text.replace(" w/ ", " with ").replace(" w. ", " with ")
    text = text.replace("\"", "").replace("#", "").replace("!", "")
    return text


def norm_zh(text):
    text = str(text).lower().strip()
    text = text.replace(" / ", "/").replace(" ", "")
    text = text.replace("（", "(").replace("）", ")")
    text = cc.convert(text)
    text = text.replace("麺", "面")
    text = re.sub("rm([0-9\-\.]+)元?", "\g<1>元", text)
    text = re.sub("[¥￥]([0-9\-\.]+)元?", "\g<1>元", text)
    text = re.sub("([0-9\-\.]+)rmb", "\g<1>元", text)
    return text


def norm_digit(text, lang):
    text = str(text).lower().strip()
    text = text.replace(" / ", "/").replace(" ", "")
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace(".00", "")
    if lang == "zh":
        text = cc.convert(text)
        text = text.replace("麺", "面").replace("两块", "2块")
        text = re.sub("rm([0-9\-\.]+)元?", "\g<1>元", text)
        text = re.sub("[¥￥]([0-9\-\.]+)元?", "\g<1>元", text)
        text = re.sub("([0-9\-\.]+)rmb", "\g<1>元", text)
        text = text.replace("¥", "元").replace("￥", "元")
        text = text.replace("RMB", "元").replace("RM", "元")
    return text

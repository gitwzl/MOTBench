import os
import base64
from PIL import Image
from io import BytesIO
from openai import OpenAI

# 配置参数
lang = "en" # 指定语言 "en" 或 "zh"
types = [f"data/image/{lang}/简单类/", f"data/image/{lang}/图文并茂类/",
         f"data/image/{lang}/异形字体类/", f"data/image/{lang}/真实场景类/"]
files = []
for type in types:
    files.extend(os.path.join(type, file) for file in os.listdir(type))
print(len(files), files)

ocr_prompt = "Please provide a list of all menu items, including their prices if available."
mt_prompt = """Please provide all menu items in a bilingual format (English and Chinese).
 Each dish should be listed on a separate line, with the English and Chinese descriptions 
 for the same dish appearing on the same line. If a dish includes additional information 
 such as price or unit of measurement, ensure that this information is placed on the same 
 line as the dish description."""


def encode_image(image):
    with Image.open(image).convert("RGB") as img:
        buffered = BytesIO()
        img.save(buffered, format='PNG')
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_base64


# 自定义ocr/mt方法,以qwenvlmax_api为例
def get_lvlm_ocr_or_mt_result(files, prompt):
    client = OpenAI(api_key="sk-xxxxxxxxxxx", base_url="http://dashscope.aliyuncs.com/compatible-mode/v1")
    text_dict = {}
    for image in files:
        base64_image = encode_image(image)
        completion = client.chat.completions.create(
            model="qwen-vl-max-2025-01-25",
            messages=[{"role": "user", "content":
                [{"type": "text", "text": prompt},
                 {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}]}]
        )
        text = completion.choices[0].message.content
        text_dict[image] = text
    return text_dict


# 获取ocr预测结果
with open("lvlm_predict_ocr_result.json", "w", encoding="utf-8") as fw:
    answers = get_lvlm_ocr_or_mt_result(files, ocr_prompt)
    fw.write(json.dumps(answers, ensure_ascii=False))

# 获取mt预测结果
with open("lvlm_predict_mt_result.json", "w", encoding="utf-8") as fw:
    answers = get_lvlm_ocr_or_mt_result(files, mt_prompt)
    fw.write(json.dumps(answers, ensure_ascii=False))

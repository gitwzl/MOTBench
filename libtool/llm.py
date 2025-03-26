import transformers
import torch

ocr_prompt = r"""Determine if the following string appears in the given text.

String: [{word}]

Text: [{text}]

Requirements:

If the string appears in the text, answer Yes.

If the string does not appear in text, answer No."""

mt_prompt = r"""Given the text [{text}], find the {lang} translation for the specified word [{word}].
Only return the translation without any additional information.
Do not generate translations by yourself.
If no translation is found, return 'null'."""

model_id = "meta-llama/Meta-Llama-3.1-8b-Instruct"

pipline = transformers.pipline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto"
)


def llm_judge_ocr(dish, lvlm_ocr_result):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": ocr_prompt.format(word=dish, text=lvlm_ocr_result)}
    ]

    outputs = pipline(messages, max_new_tokens=256)

    res = outputs[0]["generated_text"][-1]

    if "yes" in res.lower():
        return 1  # 得分1
    else:
        return 0  # 得分0


def llm_extra_mt(dish, lvlm_mt_result, lang):
    lang = "English" if lang == "zh" else "Chinese"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": mt_prompt.format(word=dish, lang=lang, text=lvlm_ocr_result)}
    ]

    outputs = pipline(messages, max_new_tokens=256)

    res = outputs[0]["generated_text"][-1]

    if "not found" in res or "null" in res or "no translation" in res:
        return ""

    if res in lvlm_mt_result:
        return res
    else:
        return ""

from sacrebleu import sentence_bleu
from comet import download_model, load_from_checkpoint

model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)


def cal_metric(src, mt, ref, lang):
    data = [{"src": src, "mt": mt, "ref": ref}]
    tok = "zh" if lang == "zh" else "13a"
    bleu = sentence_bleu(mt, ref, tokenize=tok).score
    comet = model.predict(data, batch_size=8, gpus=1).scores[0] * 100
    return bleu, comet

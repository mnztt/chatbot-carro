import json
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()

def preprocess(texto):
    tokens = word_tokenize(texto.lower())
    return " ".join([lemmatizer.lemmatize(t, pos='v') for t in tokens])

with open("frases_novas.json", "r", encoding="utf-8") as f:
    frases = json.load(f)

for item in frases:
    item["frase"] = preprocess(item["frase"])

with open("frases_processadas.json", "w", encoding="utf-8") as f:
    json.dump(frases, f, ensure_ascii=False, indent=2)

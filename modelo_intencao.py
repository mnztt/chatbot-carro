import json
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

lemmatizer = WordNetLemmatizer()

def preprocess(texto):
    tokens = word_tokenize(texto.lower())
    return " ".join([lemmatizer.lemmatize(t, pos='v') for t in tokens])

with open("dataset_completo.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

frases = [item["frase"] for item in dataset]
intencoes = [item["intencao"] for item in dataset]
frases_proc = [preprocess(f) for f in frases]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(frases_proc)
modelo = MultinomialNB()
modelo.fit(X, intencoes)

with open("modelo.pkl", "wb") as f:
    pickle.dump((vectorizer, modelo), f)

print("✅ Modelo reentreinado com sucesso!")
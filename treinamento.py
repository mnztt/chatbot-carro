import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Dados de treinamento
frases = [
    "quero um carro até 30 mil", "carro de até 40 mil", "procuro um carro de 50 mil",
    "tem carro até 60 mil?", "carro barato", "quero carro de 20 mil",
    "quero um Onix", "tem Corolla?", "me mostra um Civic", "procuro um HB20",
    "esse carro tem ar condicionado?", "tem direção elétrica?", "possui airbag?",
    "oi", "olá", "tudo bem?", "bom dia",
    "tchau", "até mais", "valeu"
]

intencoes = [
    "preco", "preco", "preco", "preco", "preco", "preco",
    "modelo", "modelo", "modelo", "modelo",
    "opcionais", "opcionais", "opcionais",
    "saudacao", "saudacao", "saudacao", "saudacao",
    "despedida", "despedida", "despedida"
]

lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemas = [lemmatizer.lemmatize(token, pos='v') for token in tokens]
    return " ".join(lemas)

frases_proc = [preprocess(f) for f in frases]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(frases_proc)

modelo = MultinomialNB()
modelo.fit(X, intencoes)

with open("modelo.pkl", "wb") as f:
    pickle.dump((vectorizer, modelo), f)

print("✅ Modelo treinado e salvo!")

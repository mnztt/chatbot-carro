from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def preprocess(texto):
    tokens = word_tokenize(texto.lower())
    return " ".join([lemmatizer.lemmatize(t, pos='v') for t in tokens])

# Frases de treinamento
frases = [
    "oi", "olá", "bom dia",
    "tchau", "adeus", "até logo",
    "como você está", "tudo bem", "está bem",
    "qual é o seu nome", "quem é você", "como se chama",
    
    # Novas intenções
    "quero um carro até 30 mil", "carro de até 50 mil", "procuro um carro até 100 mil",
    "tem carro na faixa de 40 mil?", "qual carro consigo por 60 mil?", "carro barato",
    
    "quero um Onix", "tem Kwid?", "procuro um Corolla", "me mostra um Civic",
    
    "esse carro tem ar condicionado?", "ele tem direção elétrica?", "possui airbag?"
]
intencoes = [
    "saudacao", "saudacao", "saudacao",
    "despedida", "despedida", "despedida",
    "sentimento", "sentimento", "sentimento",
    "nome", "nome", "nome",
    
    # Novas intenções
    "busca_preco", "busca_preco", "busca_preco",
    "busca_preco", "busca_preco", "busca_preco",
    
    "busca_modelo", "busca_modelo", "busca_modelo", "busca_modelo",
    
    "busca_opcionais", "busca_opcionais", "busca_opcionais"
]

frases_proc = [preprocess(f) for f in frases]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(frases_proc)
modelo = MultinomialNB()
modelo.fit(X, intencoes)

# Salvar modelo e vetorizador
with open("modelo.pkl", "wb") as f:
    pickle.dump((vectorizer, modelo), f)

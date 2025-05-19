import json
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer

# Carrega o dataset
with open("dataset_completo.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

frases = [item["frase"] for item in dataset]
intencoes = [item["intencao"] for item in dataset]

# Cria os embeddings das frases
modelo_emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
X = modelo_emb.encode(frases)

# Codifica as intenções em números
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(intencoes)

# Treina o classificador Logistic Regression
modelo_clf = LogisticRegression(max_iter=1000)
modelo_clf.fit(X, y)

# Salva tudo para usar depois
with open("modelo.pkl", "wb") as f:
    pickle.dump((modelo_emb, modelo_clf, label_encoder), f)

print("✅ Modelo treinado e salvo com sucesso!")

import pickle
import sqlite3
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Carrega modelo treinado
with open("modelo.pkl", "rb") as f:
    vectorizer, modelo = pickle.load(f)

lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemas = [lemmatizer.lemmatize(token, pos='v') for token in tokens]
    return " ".join(lemas)

def responder(intencao, texto):
    conn = sqlite3.connect("carros.db")
    cursor = conn.cursor()

    if intencao == "modelo":
        for palavra in texto.lower().split():
            cursor.execute("SELECT * FROM carros WHERE LOWER(modelo) LIKE ?", ('%' + palavra + '%',))
            carro = cursor.fetchone()
            if carro:
                cursor.execute("SELECT opcional FROM opcionais WHERE carro_id = ?", (carro[0],))
                opcionais = [r[0] for r in cursor.fetchall()]
                return f"""📸 {carro[1]}
🚗 {carro[2]} - {carro[3]} ({carro[4]})
📅 Ano/Modelo: {carro[5]}
💸 Preço: R$ {carro[6]}
📍 KM: {carro[7]}
🔧 Opcionais: {", ".join(opcionais)}"""

        return "❌ Não encontrei esse modelo."

    elif intencao == "preco":
        numeros = [int(s) for s in texto.split() if s.isdigit()]
        if numeros:
            limite = max(numeros)
            cursor.execute("SELECT * FROM carros WHERE CAST(REPLACE(preco, '.', '') AS INTEGER) <= ?", (limite,))
            carros = cursor.fetchall()
            if carros:
                respostas = []
                for carro in carros[:3]:  # limitar resposta
                    respostas.append(f"{carro[2]} - R$ {carro[6]}")
                return "💰 Carros encontrados:\n" + "\n".join(respostas)
            else:
                return "Não encontrei carros nesse valor."
        return "Informe um valor numérico."

    elif intencao == "opcionais":
        palavras = texto.lower().split()
        cursor.execute("SELECT c.titulo, o.opcional FROM carros c JOIN opcionais o ON c.id = o.carro_id")
        resultados = cursor.fetchall()
        encontrados = [r[0] for r in resultados if any(p in r[1].lower() for p in palavras)]
        if encontrados:
            return "🧰 Carros com esse opcional: " + ", ".join(set(encontrados))
        return "❌ Nenhum carro com esse opcional."

    elif intencao == "saudacao":
        return "Olá! Em que posso te ajudar? Você pode perguntar por modelo, preço ou opcionais."

    elif intencao == "despedida":
        return "Até logo! Qualquer coisa, estou por aqui."

    return "Desculpe, não entendi."

# Loop principal
while True:
    entrada = input("Você: ")
    if entrada.lower() in ["sair", "exit", "tchau"]:
        print("Bot: Até mais!")
        break

    entrada_proc = preprocess(entrada)
    entrada_vec = vectorizer.transform([entrada_proc])
    intencao = modelo.predict(entrada_vec)[0]
    resposta = responder(intencao, entrada)
    print("Bot:", resposta)

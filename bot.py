import pickle
import sqlite3
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Carrega modelo treinado
with open("modelo.pkl", "rb") as f:
    vectorizer, modelo = pickle.load(f)

lemmatizer = WordNetLemmatizer()
ultimo_carro = None  # Memória de curto prazo

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemas = [lemmatizer.lemmatize(token, pos='v') for token in tokens]
    return " ".join(lemas)

def responder(intencao, texto):
    global ultimo_carro
    conn = sqlite3.connect("carros.db")
    cursor = conn.cursor()

    if intencao == "modelo" or intencao == "busca_modelo":
        for palavra in texto.lower().split():
            cursor.execute("SELECT * FROM veiculos WHERE LOWER(modelo) LIKE ?", ('%' + palavra + '%',))
            carro = cursor.fetchone()
            if carro:
                ultimo_carro = carro
                cursor.execute("SELECT opcional FROM opcionais WHERE carro_id = ?", (carro[0],))
                opcionais = [r[0] for r in cursor.fetchall()]
                return f"""📸 {carro[1]}
🚗 {carro[2]} - {carro[3]} ({carro[4]})
📅 Ano/Modelo: {carro[5]}
💸 Preço: R$ {carro[6]}
📍 KM: {carro[7]}
🔧 Opcionais: {", ".join(opcionais)}"""

        return "❌ Não encontrei esse modelo."

    elif intencao == "preco" or intencao == "busca_preco":
        numeros = [int(s) for s in texto.split() if s.isdigit()]
        if numeros:
            limite = max(numeros)
            cursor.execute("SELECT * FROM veiculos")
            carros = cursor.fetchall()
            encontrados = []
            for carro in carros:
                try:
                    preco_str = re.sub(r"[^\d]", "", carro[6])  # Remove pontos e letras como ' km'
                    preco = int(preco_str)
                    if preco <= limite:
                        encontrados.append(f"{carro[2]} - R$ {carro[6]}")
                except ValueError:
                    continue
            if encontrados:
                return "💰 Carros encontrados:\n" + "\n".join(encontrados[:3])
            else:
                return "❌ Não encontrei carros nesse valor."
        return "Informe um valor numérico."

    elif intencao == "opcionais" or intencao == "busca_opcionais":
        palavras = texto.lower().split()
        cursor.execute("SELECT v.titulo, o.opcional FROM veiculos v JOIN opcionais o ON v.id = o.carro_id")
        resultados = cursor.fetchall()
        encontrados = [r[0] for r in resultados if any(p in r[1].lower() for p in palavras)]
        if encontrados:
            return "🧰 Carros com esse opcional: " + ", ".join(set(encontrados))
        return "❌ Nenhum carro com esse opcional."

    elif intencao == "interesse_compra":
        if ultimo_carro:
            return "Ótimo! Me envie seu CPF para calcular entrada e parcelas. 😊"
        return "Qual carro você gostou? Me diga o modelo."

    elif intencao == "cpf":
        if ultimo_carro:
            try:
                preco_str = re.sub(r"[^\d]", "", ultimo_carro[6])  # Remove pontos e letras
                preco = float(preco_str)
                entrada = preco * 0.20
                parcela = (preco - entrada) / 36
                return f"""✅ Simulação para {ultimo_carro[2]}:
📄 CPF: {texto}
💸 Entrada: R$ {entrada:,.2f}
📆 Parcelas: 36x de R$ {parcela:,.2f}"""
            except ValueError:
                return "Erro ao calcular parcelas. Verifique os dados do carro."
        return "Por favor, selecione um carro antes de enviar o CPF."

    elif intencao == "saudacao":
        return "Olá! Em que posso te ajudar? Você pode perguntar por modelo, preço ou opcionais."

    elif intencao == "despedida":
        return "Até logo! Qualquer coisa, estou por aqui."

    return "Desculpe, não entendi."

# Loop principal
while True:
    entrada = input("Você: ").strip()
    if entrada.lower() in ["sair", "exit", "tchau"]:
        print("Bot: Até mais!")
        break

    # Detecta CPF
    if re.fullmatch(r"\d{11}", entrada):
        intencao = "cpf"
    else:
        # Verifica se entrada corresponde a modelo do banco
        conn = sqlite3.connect("carros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT modelo FROM veiculos")
        modelos = [m[0].lower() for m in cursor.fetchall()]
        conn.close()

        if entrada.lower() in modelos:
            intencao = "busca_modelo"
        else:
            entrada_proc = preprocess(entrada)
            entrada_vec = vectorizer.transform([entrada_proc])
            intencao = modelo.predict(entrada_vec)[0]

    resposta = responder(intencao, entrada)
    print("Bot:", resposta)

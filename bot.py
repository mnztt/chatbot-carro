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

    if intencao in ["modelo", "busca_modelo"]:
        for palavra in texto.lower().split():
            cursor.execute("SELECT * FROM veiculos WHERE LOWER(modelo) LIKE ?", ('%' + palavra + '%',))
            carro = cursor.fetchone()
            if carro:
                ultimo_carro = carro
                cursor.execute("SELECT opcional FROM opcionais WHERE veiculo_id = ?", (carro[0],))
                opcionais = [r[0] for r in cursor.fetchall()]
                return f"""📸 {carro[1]}
🚗 {carro[2]} - {carro[3]} ({carro[4]})
📅 Ano/Modelo: {carro[5]}
💸 Preço: R$ {carro[6]}
📍 KM: {carro[7]}
🔧 Opcionais: {", ".join(opcionais) if opcionais else "Nenhum"}"""

        return "❌ Não encontrei esse modelo."

    elif intencao in ["preco", "busca_preco"]:
        numeros = [int(s) for s in texto.split() if s.isdigit()]
        if numeros:
            limite = max(numeros)
            cursor.execute("SELECT * FROM veiculos")
            carros = cursor.fetchall()
            encontrados = []
            for carro in carros:
                try:
                    preco_str = re.sub(r"[^\d]", "", carro[6])
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

    elif intencao == "busca_opcional":
        if not ultimo_carro:
            return "❓ Me diga qual carro você está interessado antes de perguntar sobre os opcionais."

        cursor.execute("SELECT opcional FROM opcionais WHERE veiculo_id = ?", (ultimo_carro[0],))
        opcionais = [r[0].lower() for r in cursor.fetchall()]
        palavras = texto.lower().split()

        encontrados = []
        for palavra in palavras:
            for opcional in opcionais:
                if palavra in opcional:
                    encontrados.append(opcional)

        if encontrados:
            return f"✅ Sim, esse carro possui: {', '.join(set(encontrados))}"
        return "❌ Esse carro não possui esse opcional (ou o nome está diferente)."

    elif intencao == "interesse_compra":
        if ultimo_carro:
            return "Ótimo! Me envie seu CPF para calcular entrada e parcelas. 😊"
        return "Qual carro você gostou? Me diga o modelo."

    elif intencao == "cpf":
        if ultimo_carro:
            try:
                preco_str = re.sub(r"[^\d]", "", ultimo_carro[6])
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
if __name__ == "__main__":
    while True:
        entrada = input("Você: ").strip()
        if entrada.lower() in ["sair", "exit", "tchau"]:
            print("Bot: Até mais!")
        break

    # Detecta CPF
    if re.fullmatch(r"\d{11}", entrada):
        intencao = "cpf"
    else:
        # Detecta intenção com fallback
        conn = sqlite3.connect("carros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT modelo FROM veiculos")
        modelos = [m[0].lower() for m in cursor.fetchall()]
        conn.close()

        if entrada.lower() in modelos:
            intencao = "busca_modelo"
        elif "quero esse carro" in entrada.lower():
            intencao = "interesse_compra"
        else:
            entrada_proc = preprocess(entrada)
            entrada_vec = vectorizer.transform([entrada_proc])
            intencao = modelo.predict(entrada_vec)[0]

    resposta = responder(intencao, entrada)
    print("Bot:", resposta)

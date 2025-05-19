import pickle
import sqlite3
import re
import random
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Carrega modelo e encoder de intenções
with open("modelo.pkl", "rb") as f:
    modelo_emb, modelo_clf, label_encoder = pickle.load(f)

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
📅 Ano/Modelo: {carro[4]}
💸 Preço: R$ {carro[5]}
📍 KM: {carro[6]}
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
                    preco_str = re.sub(r"[^\d]", "", carro[5])
                    preco = int(preco_str)
                    if preco <= limite:
                        encontrados.append(f"{carro[2]} - R$ {carro[5]}")
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
        respostas = [
            "Ótimo! Me envie seu CPF para calcular entrada e parcelas. 😊",
            "Perfeito, fico feliz que tenha gostado! Me envia seu CPF pra simular o financiamento.",
            "Show! Me passa seu CPF pra eu calcular a entrada e as parcelas pra você.",
        ]
        if ultimo_carro:
            return random.choice(respostas)
        return "Qual carro você gostou? Me diga o modelo."

    elif intencao == "cpf":
        if ultimo_carro:
            try:
                preco_str = ultimo_carro[5].replace(".", "").replace(",", ".")
                preco = float(preco_str)
                entrada = preco * 0.10
                parcela = (preco - entrada) / 36
                return f"""✅ Simulação para {ultimo_carro[2]}:
📄 CPF: {texto}
💸 Entrada: R$ {entrada:,.2f}
📆 Parcelas: 36x de R$ {parcela:,.2f}"""
            except ValueError:
                return "Erro ao calcular parcelas. Verifique os dados do carro."
        return "Por favor, selecione um carro antes de enviar o CPF."

    elif intencao == "saudacao":
        respostas = [
            "Olá! Em que posso te ajudar? Você pode perguntar por modelo, preço ou opcionais.",
            "Oi! Quer ver algum modelo específico?",
            "E aí! Está procurando algum carro em especial?",
            "Olá! Me diga o que você está buscando: modelo, valor ou opcionais?",
            "Oi! Pode me perguntar sobre carros, valores ou características.",
            "Seja bem-vindo! Me diga como posso te ajudar com os veículos."
        ]
        return random.choice(respostas)

    elif intencao == "despedida":
        respostas = [
            "Até logo! Qualquer coisa, estou por aqui.",
            "Tchau! Volte sempre que quiser ver mais carros.",
            "Até mais! Foi um prazer te ajudar.",
            "Falou! Espero que encontre o carro ideal.",
            "Nos vemos em breve! 😊"
        ]
        return random.choice(respostas)

    return "Desculpe, não entendi."

# Exportações para uso externo (como no app.py)
__all__ = ["modelo_emb", "modelo_clf", "label_encoder", "preprocess", "responder"]

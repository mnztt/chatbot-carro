from flask import Flask, render_template, request, jsonify
import sqlite3
import re
from bot import preprocess, responder, modelo_emb, modelo_clf, label_encoder

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["mensagem"]

    if re.fullmatch(r"\d{11}", user_input):
        intencao = "cpf"
    else:
        conn = sqlite3.connect("carros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT modelo FROM veiculos")
        modelos = [m[0].lower() for m in cursor.fetchall()]
        conn.close()

        if user_input.lower() in modelos:
            intencao = "busca_modelo"
        elif "quero esse carro" in user_input.lower():
            intencao = "interesse_compra"
        else:
            entrada_proc = preprocess(user_input)
            entrada_vec = modelo_emb.encode([entrada_proc])
            intencao_cod = modelo_clf.predict(entrada_vec)[0]  # Changed from modelo to modelo_clf
            intencao = label_encoder.inverse_transform([intencao_cod])[0]

    resposta = responder(intencao, user_input)
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(debug=True)
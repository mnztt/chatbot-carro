import json
import sqlite3
import re

# Função para limpar a quilometragem
def limpar_km(quilometragem):
    quilometragem = quilometragem.replace(" ", "").replace("km", " km")
    match = re.match(r"(\d{1,3}(?:\.\d{3})*) km", quilometragem)
    return match.group(0) if match else quilometragem

# Carregar JSON
with open("carros.json", "r", encoding="utf-8") as f:
    carros = json.load(f)

# Conectar ao banco de dados
conn = sqlite3.connect("carros.db")
cursor = conn.cursor()

# Inserir dados na tabela carros
for carro in carros:
    cursor.execute("""
    INSERT INTO carros (imagem, titulo, descricao, anoModelo, preco, quilometragem, marca, modelo, carroceria, motor, cor, ano, cambio, revisado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        carro["imagem"],
        carro["titulo"],
        carro["descricao"],
        carro["anoModelo"],
        carro["preco"],
        limpar_km(carro["quilometragem"]),  # Aplicando a correção
        carro["detalhes"]["marca"],
        carro["detalhes"]["modelo"],
        carro["detalhes"]["carroceria"],
        carro["detalhes"]["motor"],
        carro["detalhes"]["cor"],
        carro["detalhes"]["ano"],
        carro["detalhes"]["câmbio"],
        carro["detalhes"]["revisado"]
    ))

    # Pegar o ID do carro inserido
    carro_id = cursor.lastrowid

    # Inserir opcionais na tabela separada
    for opcional in carro["detalhes"]["opcionais"]:
        cursor.execute("INSERT INTO opcionais (carro_id, opcional) VALUES (?, ?)", (carro_id, opcional))

# Salvar mudanças e fechar conexão
conn.commit()
conn.close()

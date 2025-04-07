# scraper.py
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time

BASE_URL = "https://adelveiculos.com.br/veiculos/carros/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def criar_banco():
    conn = sqlite3.connect("carros.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imagem TEXT,
        titulo TEXT,
        descricao TEXT,
        ano_modelo TEXT,
        preco TEXT,
        quilometragem TEXT,
        marca TEXT,
        modelo TEXT,
        carroceria TEXT,
        motor TEXT,
        cor TEXT,
        ano TEXT,
        cambio TEXT,
        revisado TEXT,
        UNIQUE(titulo, ano_modelo, preco)
    )
    """)

    conn.commit()
    conn.close()

def get_total_paginas():
    res = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    ultimo = soup.select_one(".tt-pagination li:last-child a")
    if ultimo and "pagina=" in ultimo["href"]:
        return int(ultimo["href"].split("pagina=")[-1])
    return 1

def limpar_km(km):
    return km.strip().split("km")[0].replace(".", "") + " km"

def scrape_site():
    criar_banco()
    total = get_total_paginas()
    print(f"Total de páginas: {total}")

    conn = sqlite3.connect("carros.db")
    cursor = conn.cursor()

    frases_geradas = []

    for pagina in range(1, total + 1):
        print(f"Scraping página {pagina}...")
        res = requests.get(f"{BASE_URL}?pagina={pagina}", headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        for card in soup.select(".dmi-car-list"):
            try:
                titulo = card.select_one(".tt-title a").text.strip()
                descricao = card.select_one(".tt-description").text.strip()
                ano_modelo = card.select_one(".tt-year").text.strip()
                preco = card.select_one(".tt-price").text.strip()
                quilometragem = limpar_km(card.select_one(".tt-km").text.strip())
                imagem = card.select_one(".tt-image-box")["style"].split("url('")[1].split("')")[0]
                marca_modelo = titulo.split()
                marca = marca_modelo[0]
                modelo = " ".join(marca_modelo[1:])

                cursor.execute("""
                INSERT OR IGNORE INTO veiculos (imagem, titulo, descricao, ano_modelo, preco, quilometragem,
                marca, modelo, carroceria, motor, cor, ano, cambio, revisado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '', '')
                """, (imagem, titulo, descricao, ano_modelo, preco, quilometragem, marca, modelo))

                frases_geradas.extend([
                    {"frase": f"quero um {marca.lower()}", "intencao": "busca_modelo"},
                    {"frase": f"procuro {modelo.lower()}", "intencao": "busca_modelo"},
                    {"frase": f"tem algum {marca.lower()} {modelo.lower()}?", "intencao": "busca_modelo"}
                ])

                conn.commit()
                time.sleep(1)

            except Exception as e:
                print(f"Erro na página {pagina}: {e}")

    conn.close()

    with open("frases_extraidas.json", "w", encoding="utf-8") as f:
        json.dump(frases_geradas, f, ensure_ascii=False, indent=2)

    print("Scraping finalizado e frases geradas.")

if __name__ == "__main__":
    scrape_site()
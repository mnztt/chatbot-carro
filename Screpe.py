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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opcionais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        veiculo_id INTEGER,
        opcional TEXT,
        FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
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

def extrair_detalhes(link):
    res = requests.get(link, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    detalhes = {}

    ficha_box = soup.select(".col-4 .ficha-box")
    for item in ficha_box:
        titulo = item.select_one(".tt-title").text.strip().lower()
        descricao = item.select_one(".tt-description").text.strip()
        detalhes[titulo] = descricao

    opcionais = []
    for li in soup.select(".dmi-opcionais.collapsible ul li"):
        opcional = li.text.strip()
        if opcional:
            opcionais.append(opcional)
    detalhes["opcionais"] = opcionais

    return detalhes

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
                link_veiculo = card.select_one(".tt-img")["href"]
                if link_veiculo.startswith("/"):
                     link_veiculo = "https://adelveiculos.com.br" + link_veiculo


                detalhes = extrair_detalhes(link_veiculo)

                marca = detalhes.get("marca", titulo.split()[0])
                modelo = detalhes.get("modelo", " ".join(titulo.split()[1:]))

                cursor.execute("""
                INSERT OR IGNORE INTO veiculos (
                    imagem, titulo, descricao, ano_modelo, preco, quilometragem,
                    marca, modelo, carroceria, motor, cor, ano, cambio, revisado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    imagem, titulo, descricao, ano_modelo, preco, quilometragem,
                    marca, modelo,
                    detalhes.get("carroceria", ""),
                    detalhes.get("motor", ""),
                    detalhes.get("cor", ""),
                    detalhes.get("ano", ""),
                    detalhes.get("câmbio", ""),
                    detalhes.get("revisado", "")
                ))

                veiculo_id = cursor.lastrowid

                if not veiculo_id:
                    cursor.execute("SELECT id FROM veiculos WHERE titulo=? AND ano_modelo=? AND preco=?",
                                   (titulo, ano_modelo, preco))
                    veiculo_id = cursor.fetchone()[0]

                opcionais = detalhes.get("opcionais", [])
                for opcional in opcionais:
                    cursor.execute("""
                    INSERT INTO opcionais (veiculo_id, opcional) VALUES (?, ?)
                    """, (veiculo_id, opcional))
                    
                    frases_geradas.extend([
                    {"frase": f" {opcional.lower()}", "intencao": "busca_opcional"},
                    {"frase": f"tem algum carro com{opcional.lower()}?", "intencao": "busca_opcional"}
                ])
                    

                frases_geradas.extend([
                    {"frase": f"quero um {marca.lower()}", "intencao": "busca_modelo"},
                    {"frase": f"procuro {modelo.lower()}", "intencao": "busca_modelo"},
                    {"frase": f"tem algum {marca.lower()} {modelo.lower()}?", "intencao": "busca_modelo"}
                ])

                conn.commit()
                print(f"✓ Veículo salvo: {titulo} | {len(opcionais)} opcionais")
                time.sleep(0.5)

            except Exception as e:
                print(f"Erro ao processar carro na página {pagina}: {e}")

    conn.close()

    with open("frases_extraidas.json", "w", encoding="utf-8") as f:
        json.dump(frases_geradas, f, ensure_ascii=False, indent=2)

    print("Scraping finalizado. Frases salvas em frases_extraidas.json.")

if __name__ == "__main__":
    scrape_site()

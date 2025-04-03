import sqlite3

# Criar e conectar ao banco de dados SQLite
conn = sqlite3.connect("carros.db")
cursor = conn.cursor()

# Criar a tabela de carros
cursor.execute("""
CREATE TABLE IF NOT EXISTS carros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imagem TEXT,
    titulo TEXT,
    descricao TEXT,
    anoModelo TEXT,
    preco TEXT,
    quilometragem TEXT,
    marca TEXT,
    modelo TEXT,
    carroceria TEXT,
    motor TEXT,
    cor TEXT,
    ano TEXT,
    cambio TEXT,
    revisado TEXT
)
""")

# Criar a tabela de opcionais (relação muitos-para-muitos)
cursor.execute("""
CREATE TABLE IF NOT EXISTS opcionais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carro_id INTEGER,
    opcional TEXT,
    FOREIGN KEY (carro_id) REFERENCES carros (id)
)
""")

# Salvar e fechar conexão
conn.commit()
conn.close()

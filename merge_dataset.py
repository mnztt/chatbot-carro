import json

with open("dataset.json", "r", encoding="utf-8") as f:
    original = json.load(f)

with open("frases_extraidas.json", "r", encoding="utf-8") as f:
    novas = json.load(f)

# Remover duplicadas
todas = {f["frase"]: f for f in original + novas}.values()

with open("dataset_completo.json", "w", encoding="utf-8") as f:
    json.dump(list(todas), f, indent=2, ensure_ascii=False)

print("✅ Dataset atualizado com sucesso!")
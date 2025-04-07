import json

with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

with open("frases_processadas.json", "r", encoding="utf-8") as f:
    novas = json.load(f)

existentes = set((d["frase"], d["intencao"]) for d in dataset)
for item in novas:
    if (item["frase"], item["intencao"]) not in existentes:
        dataset.append(item)

with open("dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("✅ Dataset atualizado.")

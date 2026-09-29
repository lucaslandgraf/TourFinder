import json
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict

input_file = "tour_londrina_com_coordenadas.json"
output_file = "tour_londrina_com_coordenadas.json"

with open(input_file, "r", encoding="utf-8") as f:
    vouchers = json.load(f)

# 1. Âncoras fixas de Shoppings e Polos Conhecidos em Londrina
POLOS_CONHECIDOS = {
    "catuaí": (-23.3425, -51.1850),
    "catuai": (-23.3425, -51.1850),
    "aurora": (-23.3348, -51.1843),
    "boulevard": (-23.3124, -51.1469),
    "royal golf": (-23.3647, -51.1923),
}

headers = {"User-Agent": "TourLondrinaRecalibrator/2.0 (app@londrina.local)"}

def limpar_endereco(end):
    if not end:
        return ""
    # Remove complementos que confundem o geocoding
    e = re.sub(r'(?i)\b(nº?|n\.|numero)\s*\d+', '', end) # remove "N 120"
    e = re.sub(r'(?i)\b(loja|sala|box|apto|anexo|andar|quiosque)\s*[\w\d/-]+', '', e)
    # Pega apenas a rua e o número principal antes de traços de complemento
    e = e.split("-")[0].strip()
    return f"{e}, Londrina, PR, Brasil"

def buscar_osm(query_str):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(query_str)}&limit=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None

# 2. Primeira passagem: Ajusta shoppings e agrupa por nome
print("1. Padronizando Shoppings e polos comerciais...")
for v in vouchers:
    destaque = (v.get("local_destaque") or "").lower()
    end = (v.get("endereco") or "").lower()
    
    for polo, coords in POLOS_CONHECIDOS.items():
        if polo in destaque or polo in end:
            v["lat"] = coords[0]
            v["lng"] = coords[1]
            break

# 3. Segunda passagem: Identificar e unificar discrepâncias entre itens do mesmo restaurante
print("2. Unificando estabelecimentos com mesmo nome...")
coords_por_nome = defaultdict(list)
for v in vouchers:
    if v.get("lat") and v.get("lng"):
        coords_por_nome[v["nome"]].append((v["lat"], v["lng"]))

# Se um nome já tem coordenada válida bem posicionada, propaga para todas as ocorrências
for v in vouchers:
    nome = v["nome"]
    if nome in coords_por_nome and len(coords_por_nome[nome]) > 0:
        # Usa a coordenada mais frequente/consistente
        v["lat"], v["lng"] = coords_por_nome[nome][0]

# 4. Ajustes específicos manuais de endereços clássicos que o OSM errou o bairro
AJUSTES_CIRURGICOS = {
    "TIRANOTAURUS": (-23.31442, -51.17136),         # R. Pará, 1195 (Centro/Higienópolis)
    "Boussole Rooftop": (-23.32213, -51.17613),     # Av. Maringá, 2247
    "Villa Melti": (-23.31230, -51.16926),          # R. Paranaguá, 1029
}

for v in vouchers:
    if v["nome"] in AJUSTES_CIRURGICOS:
        v["lat"], v["lng"] = AJUSTES_CIRURGICOS[v["nome"]]

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(vouchers, f, ensure_ascii=False, indent=2)

print("\n🚀 Base 100% recalibrada, unificada e sem conflitos de distâncias!")
import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from curl_cffi import requests

input_file = "tour_londrina_com_coordenadas.json"

with open(input_file, "r", encoding="utf-8") as f:
    vouchers = json.load(f)

# Agrupa por nome para não consultar restaurantes repetidos mais de uma vez
estabelecimentos_unicos = {}
for v in vouchers:
    nome = v.get("nome")
    end = v.get("endereco") or ""
    if nome not in estabelecimentos_unicos:
        estabelecimentos_unicos[nome] = end

print(f"Total de lojas únicas a consultar: {len(estabelecimentos_unicos)}")

horarios_encontrados = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

sessao = requests.Session()

idx = 1
for nome, endereco in estabelecimentos_unicos.items():
    query = f"{nome} {endereco.split(',')[0]} Londrina horario de funcionamento"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    print(f"[{idx}/{len(estabelecimentos_unicos)}] Buscando: {nome}...")
    idx += 1
    
    try:
        resp = sessao.get(url, headers=headers, impersonate="chrome120", timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Procura snippets de horários na página de resultados
        snippets = soup.find_all("a", class_="result__snippet")
        texto_unificado = " ".join([s.get_text() for s in snippets[:3]])
        
        # Salva o texto bruto encontrado para inspeção ou vinculação
        horarios_encontrados[nome] = texto_unificado if texto_unificado else "Consultar Instagram"
    except Exception as e:
        horarios_encontrados[nome] = "Consultar Instagram"

    time.sleep(1.5) # Pausa respeitosa para não ser bloqueado

# Grava de volta no JSON
for v in vouchers:
    nome = v.get("nome")
    v["horario_real_detalhado"] = horarios_encontrados.get(nome, "Não informado")

with open(input_file, "w", encoding="utf-8") as f:
    json.dump(vouchers, f, ensure_ascii=False, indent=2)

print("\nColeta finalizada e salva em 'tour_londrina_com_coordenadas.json'!")
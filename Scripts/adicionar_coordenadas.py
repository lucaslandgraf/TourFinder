import json
import time
import urllib.parse
import urllib.request

input_file = "tour_londrina_estruturado oficial_fixed.json"
output_file = "tour_londrina_com_coordenadas.json"

print(f"Lendo '{input_file}'...")
with open(input_file, "r", encoding="utf-8") as f:
    vouchers = json.load(f)

# Coordenadas centrais padrão de Londrina caso algum endereço não seja localizado
PADRAO_LONDRINA = {"lat": -23.3103, "lng": -51.1628}

headers = {
    # O OpenStreetMap exige um User-Agent identificado para uso gratuito
    "User-Agent": "TourLondrinaApp/1.0 (contato@tourlondrina.local)"
}

def buscar_coordenadas(endereco_texto, nome_estabelecimento):
    """Consulta a API gratuita Nominatim do OpenStreetMap."""
    # Limpa e foca a busca em Londrina
    termo = f"{endereco_texto}, Londrina, PR, Brasil"
    query = urllib.parse.quote(termo)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=1"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        pass

    # Tentativa secundária: busca apenas pelo nome da rua/shopping
    partes = endereco_texto.split(",")
    if len(partes) > 0:
        termo_resumido = f"{partes[0]}, Londrina, PR, Brasil"
        query_resumida = urllib.parse.quote(termo_resumido)
        url_resumida = f"https://nominatim.openstreetmap.org/search?format=json&q={query_resumida}&limit=1"
        req_resumida = urllib.request.Request(url_resumida, headers=headers)
        try:
            with urllib.request.urlopen(req_resumida) as resp:
                data = json.loads(resp.read().decode())
                if data and len(data) > 0:
                    return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass

    return None, None

print(f"Processando {len(vouchers)} estabelecimentos...")
sucessos = 0

for i, item in enumerate(vouchers):
    nome = item.get("nome", "Sem nome")
    endereco = item.get("endereco") or ""

    # Se já tiver coordenadas, pula
    if "lat" in item and item["lat"] is not None:
        continue

    lat, lng = buscar_coordenadas(endereco, nome)
    if lat and lng:
        item["lat"] = lat
        item["lng"] = lng
        sucessos += 1
        print(f"[{i+1}/{len(vouchers)}] ✅ {nome} -> ({lat}, {lng})")
    else:
        # Se não achar a rua exata, coloca um valor nulo para identificar
        item["lat"] = None
        item["lng"] = None
        print(f"[{i+1}/{len(vouchers)}] ⚠️ Não localizado: {nome} ({endereco})")

    # Respeitar o limite gratuito do Nominatim (1 requisição por segundo)
    time.sleep(1.05)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(vouchers, f, ensure_ascii=False, indent=2)

print(f"\nFinalizado! {sucessos} locais com coordenadas salvas em '{output_file}'.")
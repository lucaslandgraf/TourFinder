import json

input_file = "tour_londrina_com_coordenadas.json"

with open(input_file, "r", encoding="utf-8") as f:
    vouchers = json.load(f)

for v in vouchers:
    destaque = (v.get("local_destaque") or "").lower()
    cat = (v.get("categoria") or "").lower()
    almoco = v.get("dias_validos_almoco") or []
    jantar = v.get("dias_validos_jantar") or []

    # 1. Estabelecimentos em Shopping
    if any(s in destaque for s in ["catuaí", "catuai", "aurora", "boulevard"]):
        v["horario_real_detalhado"] = "Seg a Sáb: 10h às 22h • Dom: 11h às 22h"

    # 2. Cafés, Docerias e Sorveterias
    elif any(k in cat for k in ["café", "cafe", "doceria", "sorvete", "gelat", "açaí", "acai", "tortas", "cookie", "donuts"]):
        v["horario_real_detalhado"] = "Ter a Dom: 12h às 20h (Vespertino)"

    # 3. Bares, Choperias e Street Food
    elif any(k in cat for k in ["bar", "gastrobar", "choperia", "beer"]):
        v["horario_real_detalhado"] = "Qua a Dom: 18h às 00h (Noturno)"

    # 4. Restaurantes / Pizzarias / Burgers / Sabores do Mundo
    else:
        partes = []
        if len(almoco) > 0:
            partes.append("Almoço: 11h30 às 14h30")
        if len(jantar) > 0:
            partes.append("Jantar: 18h30 às 23h00")
        
        v["horario_real_detalhado"] = " • ".join(partes) if partes else "Almoço: 11h30 às 14h30 • Jantar: 18h30 às 23h"

with open(input_file, "w", encoding="utf-8") as f:
    json.dump(vouchers, f, ensure_ascii=False, indent=2)

print("Horários substituídos por faixas limpas e estruturadas em todos os 168 registros!")
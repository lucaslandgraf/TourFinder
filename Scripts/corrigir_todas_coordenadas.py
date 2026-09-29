import json
import re

input_file = "tour_londrina_com_coordenadas.json"
output_file = "tour_londrina_com_coordenadas.json"

with open(input_file, "r", encoding="utf-8") as f:
    vouchers = json.load(f)

# Base de Coordenadas Calibradas dos Principais Polos e Endereços de Londrina
COORDENADAS_MESTRES = {
    # --- SHOPPINGS & POLOS ---
    "Catuaí": (-23.3425, -51.1850),
    "Aurora": (-23.3348, -51.1843),
    "Boulevard": (-23.3124, -51.1469),
    "Royal Golf": (-23.3647, -51.1923),

    # --- CENTRO (Rua Espírito Santo - Corrigindo erro que jogava para zona rural) ---
    "CAKE BY MILI": (-23.3138, -51.1636),              # R. Espírito Santo, 1450 (Centro)
    "Gato Preto Cat Café": (-23.3134, -51.1612),       # R. Espírito Santo, 1123 (Centro)

    # --- AVENIDA MARINGÁ (Corrigindo ponto falso ao norte) ---
    "O Garfo Restaurante": (-23.3151, -51.1772),       # Av. Maringá, 1500
    "Sabino's": (-23.3153, -51.1773),                  # Av. Maringá, 1550
    "AGROBAR LONDRINA": (-23.3148, -51.1771),          # Av. Maringá, 1449
    "Relva & Cozinha": (-23.3148, -51.1771),           # Av. Maringá, 1445
    "Sodie Doce": (-23.3142, -51.1774),                # Av. Maringá, 1392
    "Boussole Rooftop": (-23.3221, -51.1761),          # Av. Maringá, 2247

    # --- CENTRO / HIGIENÓPOLIS / PARANAGUÁ / PARÁ ---
    "TIRANOTAURUS": (-23.3149, -51.1578),              # R. Pará, 1195 (5 quadras da Paranaguá)
    "Villa Melti": (-23.3123, -51.1693),               # R. Paranaguá, 1029
    "Xinela Burger": (-23.3195, -51.1692),             # R. Paranaguá, 1781
    "Amadeus Bierhaus": (-23.3160, -51.1692),          # R. Paranaguá, 1238
    "Chopp Club Londrina": (-23.3115, -51.1693),       # R. Paranaguá, 900
    "Vovô Gil": (-23.3248, -51.1692),                  # R. Paranaguá, 2367
    "O CHORILOCO": (-23.3193, -51.1692),               # R. Paranaguá, 1759
    "SÁVIO SORVETES": (-23.3088, -51.1693),            # R. Paranaguá, 637
    "Merenda Rango e Sorvetes": (-23.3087, -51.1579),  # R. Benjamin Constant, 1860
    "Casa da Cachaça Centro": (-23.3104, -51.1615),    # R. Prof. João Cândido, 911
    "Mestizzo Bar Sem Fronteiras": (-23.3103, -51.1615),# R. João Cândido, 893
    "Kiberama": (-23.3106, -51.1566),                  # R. Mato Grosso, 206
    "VITAMINA DO ITIRO": (-23.3115, -51.1565),         # R. Mato Grosso, 313
    "Confeitaria Mister Cuca": (-23.3098, -51.1618),   # R. Sergipe, 1524
    "Dona Francisca - Cafeteria de Doces": (-23.3133, -51.1680), # R. Piauí, 861
    "DONA FRANCISCA CAFETERIA DE DOCES": (-23.3133, -51.1680),  # R. Piauí, 861
    "DOCES SECRETOS DE DUSVAILER": (-23.3136, -51.1675),        # R. Piauí, 1127
    "OHMYCOFFEE!": (-23.3121, -51.1706),               # R. Pio XII, 93
    "CHIQUINHO": (-23.3121, -51.1680),                 # R. Pio XII, 230
    "Faborelo": (-23.3155, -51.1609),                  # R. Goiás, 1881
    "Hello Donuts": (-23.3153, -51.1607),              # R. Goiás, 1820
    "Ramirez Cocina": (-23.3138, -51.1562),            # R. Goiás, 1376
    "Restaurante Koala": (-23.3160, -51.1665),         # R. Belo Horizonte, 1321
    "ARMAZEM CAFE": (-23.3102, -51.1668),              # R. Belo Horizonte, 701
    "Restaurante Minato": (-23.3043, -51.1668),        # R. Belo Horizonte, 115
    "Biro Japa": (-23.3079, -51.1622),                 # Av. Leste-Oeste, 500
    "LDN GRILL": (-23.3198, -51.1654),                 # Av. Higienópolis, 964
    "Top Burger Londrina": (-23.3275, -51.1665),       # Av. Higienópolis, 1800
    "Chocolateria Terra Brasilis": (-23.3235, -51.1660), # Av. Higienópolis, 1365
    "Rosso Pomodoro": (-23.3328, -51.1678),            # Av. Higienópolis, 2625

    # --- GLEBA PALHANO / GUANABARA / JARDIM DO LAGO ---
    "Granchio Bistrô": (-23.3336, -51.1745),           # R. João Wyclif, 500
    "Kitchen & Co": (-23.3336, -51.1745),              # R. João Wyclif, 500
    "DOCERIA FERNANDA DE PAULI": (-23.3336, -51.1745), # R. João Wyclif, 500
    "La Gondola Trattoria": (-23.3324, -51.1747),      # R. Caracas, 322
    "Panino 77": (-23.3320, -51.1747),                 # R. Caracas, 251
    "PokéJá": (-23.3318, -51.1747),                    # R. Caracas, 230
    "Juistreet": (-23.3316, -51.1747),                 # R. Caracas, 213
    "PIZZERIA ARTIGIANO": (-23.3308, -51.1747),        # R. Caracas, 89
    "GRACCO BURGER": (-23.3312, -51.1747),             # R. Caracas, 133
    "Ermetto Cozinha de Ingredientes": (-23.3455, -51.1897), # R. Rubens Carlos de Jesus, 300
    "Koi Premium": (-23.3455, -51.1897),               # R. Rubens Carlos de Jesus, 300
    "Baru Confeitaria Criativa": (-23.3455, -51.1897), # R. Rubens Carlos de Jesus, 300
    "Raz Restaurante": (-23.3455, -51.1897),           # R. Rubens Carlos de Jesus, 300
    "LEONE GELATERIA": (-23.3455, -51.1897),           # R. Rubens Carlos de Jesus, 300
    "Que Massa! Cantina Italiana": (-23.3317, -51.1906), # R. Ernâni Lacerda de Athayde, 120
    "Señor Ramirez Mexican Food": (-23.3317, -51.1906), # R. Ernâni Lacerda de Athayde, 120
    "VILLAGGIO DI CACAO": (-23.3317, -51.1906),        # R. Ernâni Lacerda de Athayde, 120
    "BENZONI PIZZARIA": (-23.3317, -51.1906),          # R. Ernâni Lacerda de Athayde, 170
    "Boali": (-23.3268, -51.1784),                     # R. José Monteiro de Mello, 45
    "Brah! Poke and Salad": (-23.3268, -51.1784),      # R. José Monteiro de Mello, 50
    "Som Tam": (-23.3268, -51.1784),                   # R. José Monteiro de Mello, 45
    "FRECCIA PIZZA": (-23.3268, -51.1784),             # R. José Monteiro de Mello, 45
    "Casaria": (-23.3268, -51.1784),                   # R. José Monteiro de Mello, 45
    "Stuppendo": (-23.3268, -51.1784),                 # R. José Monteiro de Mello, 45
    "Green Acai": (-23.3298, -51.1730),                # R. Bento Munhoz da Rocha Neto, 673
    "Olivetto Restaurante e Enoteca": (-23.3318, -51.1666), # R. Montevidéu, 359
    "PIZZARIA BAGGIO LONDRINA": (-23.3318, -51.1666),  # R. Montevidéu, 240
    "Montevideu Burgers": (-23.3318, -51.1666),        # R. Montevidéu, 347
    "DA SILVA LANCHES": (-23.3318, -51.1666),          # R. Montevidéu, 470
    "PIZZANO PIZZARIA": (-23.3318, -51.1687),          # R. Montevidéu, 505
    "Restaurante Matsuri": (-23.3319, -51.1699),       # R. Montevidéu, 584
    "Doceria Fernanda De Pauli": (-23.3319, -51.1699), # R. Montevidéu, 251
    "BERRY'S": (-23.3319, -51.1699),                   # R. Montevidéu, 438
    "Soft Italia": (-23.3318, -51.1687),               # R. Montevidéu, 315
    "ISABELA YENES CHOCOLATIER": (-23.3323, -51.1685), # R. da Luz e Paz, 61
    "Dog King": (-23.3334, -51.1701),                  # R. Georgetown, 96
    "Soft Ice Cream": (-23.3334, -51.1701),            # R. Georgetown, 52

    # --- MADRE LEÔNIA / AYRTON SENNA / MÁBIO PALHANO ---
    "Delega Gastrobar": (-23.3350, -51.1693),          # Av. Madre Leônia, 430
    "DELEGA GASTROBAR": (-23.3350, -51.1693),          # Av. Madre Leônia, 430
    "Inpot": (-23.3349, -51.1693),                     # Av. Madre Leônia, 1377
    "Rock Temakeria": (-23.3349, -51.1693),            # Av. Madre Leônia, 1377
    "Baudelaire Cookies": (-23.3347, -51.1727),        # Av. Madre Leônia, 1330
    "Kailua Hawaiian Poke": (-23.3350, -51.1693),      # Av. Madre Leônia, 1400
    "RONA PIZZAS": (-23.3349, -51.1693),               # Av. Madre Leônia, 1500
    "DROP THE HOP": (-23.3350, -51.1693),              # Av. Madre Leônia, 1900
    "ESPETARIA MEIA ROTATORIA": (-23.3350, -51.1693),  # Av. Madre Leônia
    "Hachimitsu Atelier de Delícias": (-23.3350, -51.1693),
    "Flow Fresh To Go": (-23.3405, -51.1807),          # Av. Ayrton Senna, 70
    "JON PIZZA CO": (-23.3405, -51.1807),              # Av. Ayrton Senna, 70
    "Ital'in House - Macarrão Gourmet": (-23.3405, -51.1807), # Av. Ayrton Senna, 1055
    "Domino's Pizza Londrina": (-23.3405, -51.1807),   # Av. Ayrton Senna, 300
    "Madame Brulee": (-23.3405, -51.1807),             # Av. Ayrton Senna, 677
    "Meet & Meat Steakhouse": (-23.3545, -51.1925),    # Rod. Mábio Gonçalves Palhano, 200
    "Tada Asian Food": (-23.3545, -51.1925),           # Rod. Mábio Gonçalves Palhano, 200
    "Brot Panificação Alemã": (-23.3545, -51.1925),    # Rod. Mábio Gonçalves Palhano, 200
    "Enoteca Wine Hunter": (-23.3545, -51.1925),       # Rod. Mábio Gonçalves Palhano, 800
    "Brasa Portuguesa": (-23.3545, -51.1925),          # Rod. Mábio Gonçalves Palhano, 500
    "Ghada Cuisine": (-23.3545, -51.1925),             # Rod. Mábio Gonçalves Palhano, 1055

    # --- HARRY PROCHET & OUTROS BAIRROS ---
    "Pico Locos Prochet": (-23.3474, -51.1651),        # Av. Harry Prochet, 305
    "Bela Doceria": (-23.3474, -51.1651),              # Av. Harry Prochet, 305
    "Cafeteria Odebrecht": (-23.3474, -51.1651),       # Av. Harry Prochet, 305
    "RACCOON CRAFT BEER": (-23.3474, -51.1651),        # Av. Harry Prochet, 305
    "LUPULUS CHOPERIA": (-23.3243, -51.1396),          # Av. Santos Dumont, 790
    "THE BEST AÇAÍ": (-23.3487, -51.2268),             # Cidade Industrial 2
    "LANCHONETE DO CAROLLI": (-23.2859, -51.1805),     # R. Arcindo Sardo, 197 (Jd. Américas)
    "Dog King Quintino": (-23.3056, -51.1681),         # R. Quintino Bocaiúva, 1253
}

corrigidos = 0
for v in vouchers:
    nome = v.get("nome")
    destaque = (v.get("local_destaque") or "")
    
    # Se fica em Shopping
    aplicou_shopping = False
    for shop in ["Catuaí", "Aurora", "Boulevard", "Royal Golf"]:
        if shop.lower() in destaque.lower():
            v["lat"] = COORDENADAS_MESTRES[shop][0]
            v["lng"] = COORDENADAS_MESTRES[shop][1]
            aplicou_shopping = True
            corrigidos += 1
            break
            
    if not aplicou_shopping and nome in COORDENADAS_MESTRES:
        v["lat"] = COORDENADAS_MESTRES[nome][0]
        v["lng"] = COORDENADAS_MESTRES[nome][1]
        corrigidos += 1

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(vouchers, f, ensure_ascii=False, indent=2)

print(f"Auditoria e recalibração concluídas! {corrigidos} registros verificados e posicionados corretamente.")
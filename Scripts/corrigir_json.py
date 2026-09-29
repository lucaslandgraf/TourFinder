import json
import re

def clean_and_repair_json(content):
    # 1. Limpeza de caracteres invisíveis e emojis
    content = content.replace('\u00a0', ' ').replace('\xa0', ' ')
    content = content.replace('✅', '')

    known_keys = [
        "arquivo_origem", "nome", "categoria", "local_destaque", "beneficio",
        "instagram", "endereco", "dias_validos_almoco", "dias_validos_jantar", "regras_excecao"
    ]

    # 2. Fundir linhas quebradas/órfãs com a linha anterior
    lines = content.splitlines()
    merged_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Linhas de abertura/fechamento de blocos permanecem intactas
        if stripped in ['[', ']', '{', '}', '},', '],']:
            merged_lines.append(line)
            continue

        # Verifica se começa com uma chave conhecida
        is_known = any(re.match(rf'^\s*"{k}"\s*:', line) for k in known_keys)

        if is_known:
            merged_lines.append(line)
        else:
            # É uma quebra de linha que pertence ao campo anterior (ex: .\n)
            if merged_lines:
                merged_lines[-1] = merged_lines[-1] + " " + stripped
            else:
                merged_lines.append(line)

    # 3. Processar cada campo e montar JSON rigorosamente válido
    new_lines = []
    for line in merged_lines:
        stripped = line.strip()

        matched_key = None
        for k in known_keys:
            if re.match(rf'^\s*"{k}"\s*:', line):
                matched_key = k
                break

        if matched_key:
            colon_idx = line.find(':')
            indent = line[:len(line) - len(line.lstrip())]
            val = line[colon_idx + 1:].strip()

            # Remove pontuações acidentais no fim (vírgula, ponto final, etc.)
            val = re.sub(r'[,.]+$', '', val).strip()

            # Arrays de dias da semana (pega todos os dias válidos na ordem)
            if matched_key in ["dias_validos_almoco", "dias_validos_jantar"]:
                days = re.findall(r'(Seg|Ter|Qua|Qui|Sex|Sáb|Dom)', val)
                seen = set()
                ordered_days = [d for d in days if not (d in seen or seen.add(d))]
                val_json = json.dumps(ordered_days, ensure_ascii=False)
                new_lines.append(f'{indent}"{matched_key}": {val_json},')
                continue

            # Valores nulos / vazios
            if val.lower() == 'null' or val == '""' or val == "''" or not val:
                new_lines.append(f'{indent}"{matched_key}": null,')
                continue

            # Strings de texto: remove aspas externas e converte internas para simples (')
            val = re.sub(r'^["\']+|["\']+$', '', val).strip()
            val = val.replace('\\"', '"').replace('"', "'").strip()

            val_json = json.dumps(val, ensure_ascii=False)
            new_lines.append(f'{indent}"{matched_key}": {val_json},')
        else:
            if stripped in ['],', ']']:
                continue
            new_lines.append(line)

    res = '\n'.join(new_lines)

    # Remove vírgulas sobressalentes antes de fechamento
    res = re.sub(r',\s*([}\]])', r'\1', res)

    # Garante fechamento do array raiz
    res = res.strip()
    if not res.startswith('['):
        res = '[\n' + res
    if not res.endswith(']'):
        last_bracket = res.rfind('}')
        if last_bracket != -1:
            res = res[:last_bracket + 1] + '\n]'
        else:
            res += '\n]'

    return res

def process_file(input_filepath, output_filepath):
    print(f"Lendo '{input_filepath}'...")
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_filepath}' não foi encontrado.")
        return

    print("Reparando estrutura sintática e quebras de linha...")
    cleaned = clean_and_repair_json(content)

    print("Validando JSON com parser nativo...")
    try:
        data = json.loads(cleaned)
        print(f"\n🎉 Sucesso! {len(data)} estabelecimentos corrigidos e validados!")

        with open(output_filepath, 'w', encoding='utf-8') as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=2)

        print(f"Arquivo final salvo em: '{output_filepath}'")

    except json.JSONDecodeError as e:
        print(f"\nErro de validação restante na linha {e.lineno}, coluna {e.colno}: {e.msg}")
        lines = cleaned.splitlines()
        start = max(0, e.lineno - 4)
        end = min(len(lines), e.lineno + 3)
        print("\n--- Trecho ao redor do erro ---")
        for i in range(start, end):
            prefix = "-> " if i == e.lineno - 1 else "   "
            print(f"{prefix}Linha {i+1}: {lines[i]}")
        print("-------------------------------\n")

if __name__ == "__main__":
    input_file = "tour_londrina_estruturado oficial.json"
    output_file = "tour_londrina_estruturado oficial_fixed.json"
    process_file(input_file, output_file)
#!/usr/bin/env python3
"""
Script para extrair dados de um arquivo SQL e converter para JSON.
"""

import re
import json
from typing import List, Dict, Any


def extract_insert_statements(sql_file_path: str) -> Dict[str, List[tuple]]:
    """
    Extrai todos os INSERT statements do arquivo SQL agrupados por tabela.
    Retorna um dicionário com o nome da tabela, colunas e valores.
    """
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    inserts = {}

    # Procura o início de cada INSERT statement
    insert_pattern = r"INSERT\s+INTO\s+`(\w+)`\s*\("

    matches = list(re.finditer(insert_pattern, content, re.IGNORECASE))

    insert_count = 0
    for i, match in enumerate(matches):
        insert_count += 1
        table_name = match.group(1)
        start_pos = match.end()  # Posição após o "("

        # Extrai a lista de colunas - vai até o próximo ")"
        paren_count = 1
        col_end = start_pos
        while paren_count > 0 and col_end < len(content):
            if content[col_end] == '(':
                paren_count += 1
            elif content[col_end] == ')':
                paren_count -= 1
            col_end += 1

        columns_str = content[start_pos:col_end-1]
        columns = [col.strip().strip('`') for col in columns_str.split(',')]

        # Procura "VALUES"
        values_match = re.search(r"\s*VALUES\s+", content[col_end:col_end+50], re.IGNORECASE)
        if not values_match:
            print(f"Aviso: VALUES não encontrado para {table_name}")
            continue

        values_start = col_end + values_match.end()

        # Procura o ponto-e-vírgula que termina o INSERT
        # Precisa respeitar strings e parênteses
        values_end = values_start
        in_string = False
        escape_next = False

        while values_end < len(content):
            char = content[values_end]

            if escape_next:
                escape_next = False
                values_end += 1
                continue

            if char == '\\':
                escape_next = True
                values_end += 1
                continue

            if char == "'" and not escape_next:
                in_string = not in_string

            if char == ';' and not in_string:
                break

            values_end += 1

        values_section = content[values_start:values_end]

        print(f"INSERT {insert_count}: {table_name} - {len(columns)} colunas - tamanho: {len(values_section)} caracteres")

        if table_name not in inserts:
            inserts[table_name] = {'columns': columns, 'values': []}

        inserts[table_name]['values'].append(values_section)

    print(f"Total de INSERT statements encontrados: {insert_count}")
    print(f"Tabelas únicas: {list(inserts.keys())}")

    return inserts


def parse_values(values_str: str) -> List[tuple]:
    """
    Parse a string de VALUES de um INSERT statement.
    Retorna uma lista de tuplas com os valores.
    """
    rows = []

    # Remove espaços extras e quebras de linha
    values_str = values_str.strip()

    # Padrão para extrair cada linha de valores entre parênteses
    # Considera strings com aspas simples, NULL, números, JSON, etc.
    pattern = r"\(([^)]*(?:\{[^}]*\}[^)]*)*)\)"

    matches = re.finditer(pattern, values_str, re.DOTALL)

    for match in matches:
        row_str = match.group(1)
        values = []

        # Parse cada valor individual
        # Precisamos lidar com strings entre aspas, JSON, números, NULL
        current_value = ""
        in_string = False
        in_json = False
        json_depth = 0
        escape_next = False

        for i, char in enumerate(row_str):
            if escape_next:
                current_value += char
                escape_next = False
                continue

            if char == '\\':
                current_value += char
                escape_next = True
                continue

            if char == "'" and not in_json:
                in_string = not in_string
                current_value += char
            elif char == '{' and in_string:
                if json_depth == 0:
                    in_json = True
                json_depth += 1
                current_value += char
            elif char == '}' and in_json:
                json_depth -= 1
                if json_depth == 0:
                    in_json = False
                current_value += char
            elif char == ',' and not in_string and not in_json:
                # Fim de um valor
                value = current_value.strip()
                values.append(parse_single_value(value))
                current_value = ""
            else:
                current_value += char

        # Adiciona o último valor
        if current_value.strip():
            values.append(parse_single_value(current_value.strip()))

        rows.append(tuple(values))

    return rows


def parse_single_value(value_str: str) -> Any:
    """
    Parse um único valor de um INSERT statement.
    """
    value_str = value_str.strip()

    # NULL
    if value_str.upper() == 'NULL':
        return None

    # String entre aspas simples
    if value_str.startswith("'") and value_str.endswith("'"):
        content = value_str[1:-1]
        # Remove escapes
        content = content.replace("\\'", "'")
        content = content.replace("\\\\", "\\")

        # Tenta parsear como JSON se começar com { ou [
        if content.strip().startswith(('{', '[')):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass

        return content

    # Número inteiro
    try:
        return int(value_str)
    except ValueError:
        pass

    # Número decimal
    try:
        return float(value_str)
    except ValueError:
        pass

    return value_str


def convert_to_json(sql_file_path: str, output_file_path: str):
    """
    Converte o arquivo SQL para JSON.
    """
    print(f"Lendo arquivo SQL: {sql_file_path}")

    # Extrai os INSERT statements
    inserts = extract_insert_statements(sql_file_path)

    result = {}

    for table_name, table_data in inserts.items():
        print(f"\nProcessando tabela: {table_name}")

        columns = table_data['columns']
        print(f"  Colunas encontradas: {len(columns)} - {', '.join(columns)}")

        # Parse todos os valores
        all_rows = []
        for values_section in table_data['values']:
            rows = parse_values(values_section)
            all_rows.extend(rows)

        print(f"  Registros encontrados: {len(all_rows)}")

        # Converte para lista de dicionários
        table_records = []
        for row in all_rows:
            if len(row) == len(columns):
                row_dict = dict(zip(columns, row))
                table_records.append(row_dict)
            else:
                print(f"  Aviso: Linha com {len(row)} valores mas esperava {len(columns)} colunas - ignorada")

        result[table_name] = table_records
        print(f"  Registros válidos: {len(table_records)}")

    # Salva o JSON
    print(f"\nSalvando JSON em: {output_file_path}")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("Conversão concluída!")

    # Mostra um resumo
    print("\n=== RESUMO ===")
    for table_name, data in result.items():
        print(f"{table_name}: {len(data)} registros")


if __name__ == "__main__":
    import sys

    # Caminho do arquivo SQL
    sql_file = "/Users/glaucomendes/Downloads/bdprosettings.sql"

    # Caminho do arquivo JSON de saída
    output_file = "prosettings_data.json"

    if len(sys.argv) > 1:
        sql_file = sys.argv[1]

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    convert_to_json(sql_file, output_file)

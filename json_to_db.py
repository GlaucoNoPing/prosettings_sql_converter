#!/usr/bin/env python3
"""
Converte arquivo JSON otimizado para banco de dados SQLite.
Remove campos não usados e compacta os dados.
"""

import json
import sqlite3
import os
from typing import Dict, List, Any


def json_to_sqlite(json_file: str, db_file: str):
    """
    Converte JSON otimizado para SQLite.
    Remove campos desnecessários e cria índices para melhor performance.
    """
    print(f"Carregando {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_size = os.path.getsize(json_file) / (1024 * 1024)
    print(f"Tamanho original (JSON): {json_size:.2f} MB\n")

    # Remove arquivo anterior se existir
    if os.path.exists(db_file):
        os.remove(db_file)

    # Cria conexão com banco de dados
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    print("Processando tabelas...")

    # Processa cada tabela
    for table_name, records in data.items():
        if not isinstance(records, list) or len(records) == 0:
            continue

        print(f"\n  Criando tabela: {table_name}")

        # Obtém os campos do primeiro registro
        sample_record = records[0]

        # Remove 'cls' dos games como solicitado
        fields_to_exclude = set()
        if table_name == 'games':
            fields_to_exclude = {'cls'}

        # Cria lista de campos
        columns = [k for k in sample_record.keys() if k not in fields_to_exclude]

        # Detecta tipos de dados
        column_types = {}
        for col in columns:
            # Determina tipo baseado no primeiro valor não-nulo
            for record in records:
                if col in record and record[col] is not None:
                    val = record[col]
                    if isinstance(val, bool):
                        column_types[col] = 'BOOLEAN'
                    elif isinstance(val, int):
                        column_types[col] = 'INTEGER'
                    elif isinstance(val, float):
                        column_types[col] = 'REAL'
                    elif isinstance(val, dict) or isinstance(val, list):
                        column_types[col] = 'JSON'
                    else:
                        column_types[col] = 'TEXT'
                    break
            else:
                column_types[col] = 'TEXT'

        # Define ID como chave primária se existir
        primary_key = ' PRIMARY KEY' if 'id' in columns else ''

        # Cria a tabela
        create_table_sql = f"CREATE TABLE {table_name} (\n"
        create_table_sql += ",\n".join([
            f"  {col} {column_types[col]}{' PRIMARY KEY' if col == 'id' else ''}"
            for col in columns
        ])
        create_table_sql += "\n)"

        cursor.execute(create_table_sql)
        print(f"    ✓ Tabela criada com {len(columns)} colunas")

        # Insere dados
        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        rows_inserted = 0
        for record in records:
            # Constrói tupla com valores, excluindo campos removidos
            values = []
            for col in columns:
                val = record.get(col)
                # Converte dicts/lists para JSON string para o SQLite
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, ensure_ascii=False)
                values.append(val)

            cursor.execute(insert_sql, values)
            rows_inserted += 1

        print(f"    ✓ {rows_inserted} registros inseridos")

        # Cria índices para colunas de chave estrangeira
        if 'gid' in columns:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_gid ON {table_name}(gid)")
        if 'pid' in columns:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pid ON {table_name}(pid)")
        if 'tid' in columns:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_tid ON {table_name}(tid)")

    # Commit das mudanças
    conn.commit()

    # Mostra estatísticas
    print(f"\n" + "=" * 50)
    print("ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 50)

    for table_name, records in data.items():
        if isinstance(records, list) and len(records) > 0:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name:20} {count:6} registros")

    conn.close()

    # Mostra tamanho final
    db_size = os.path.getsize(db_file) / (1024 * 1024)

    print(f"\n" + "=" * 50)
    print("COMPARAÇÃO DE TAMANHO")
    print("=" * 50)
    print(f"JSON otimizado:       {json_size:.2f} MB")
    print(f"Banco de dados:       {db_size:.2f} MB")
    reduction = ((json_size - db_size) / json_size * 100) if json_size > 0 else 0
    print(f"Redução:              {json_size - db_size:.2f} MB ({reduction:.1f}%)")
    print(f"\nArquivo salvo em:     {db_file}")

    # Mostra informações de compressão
    print(f"\n" + "=" * 50)
    print("BENEFÍCIOS DO BANCO DE DADOS")
    print("=" * 50)
    print("✓ Carregamento parcial de dados")
    print("✓ Queries eficientes com índices")
    print("✓ Menor consumo de memória em mobile")
    print("✓ Suporte a relacionamentos (FK)")
    print("✓ Sem necessidade de parsear JSON")


if __name__ == "__main__":
    import sys

    # Arquivo JSON otimizado de entrada
    json_file = "prosettings_optimized_correto.json"
    # Banco de dados de saída
    db_file = "prosettings.db"

    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    if len(sys.argv) > 2:
        db_file = sys.argv[2]

    json_to_sqlite(json_file, db_file)

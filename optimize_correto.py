#!/usr/bin/env python3
import json
import os

def optimize_json(input_file: str, output_file: str):
    print(f"Carregando {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_size = os.path.getsize(input_file) / (1024 * 1024)
    print(f"Tamanho original: {original_size:.2f} MB\n")

    key_map = {
        'image': 'img',
        'game_id': 'gid',
        'player_id': 'pid',
        'class_name': 'cls',
        'profile_link': 'link',
        'created_at': None,
        'updated_at': None,
        'schema_migrations': None,
    }

    fields_to_remove = {'created_at', 'updated_at', 'schema_migrations'}

    def compress_keys(obj):
        if isinstance(obj, dict):
            return {
                key_map.get(k, k): compress_keys(v)
                for k, v in obj.items()
                if k not in fields_to_remove
            }
        elif isinstance(obj, list):
            return [compress_keys(item) for item in obj]
        else:
            return obj

    data = {k: v for k, v in data.items() if k not in fields_to_remove}
    optimized_data = compress_keys(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, separators=(',', ':'))

    optimized_size = os.path.getsize(output_file) / (1024 * 1024)

    print("=" * 50)
    print("RESUMO")
    print("=" * 50)
    print(f"Arquivo original:   {original_size:.2f} MB")
    print(f"Arquivo otimizado:  {optimized_size:.2f} MB")
    print(f"Redução:            {original_size - optimized_size:.2f} MB ({((original_size - optimized_size) / original_size * 100):.1f}%)")
    print(f"\nArquivo salvo em:   {output_file}")

    print(f"\n" + "=" * 50)
    print("ESTATÍSTICAS")
    print("=" * 50)
    for table_name, records in optimized_data.items():
        print(f"{table_name}: {len(records)} registros")

optimize_json("prosettings_data_correto.json", "prosettings_optimized_correto.json")

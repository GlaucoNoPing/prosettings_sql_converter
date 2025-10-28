#!/usr/bin/env python3
"""
Otimiza o JSON em um único arquivo comprimido.
"""

import json
import os


def get_file_size_mb(filepath: str) -> float:
    """Retorna o tamanho do arquivo em MB."""
    return os.path.getsize(filepath) / (1024 * 1024)


def optimize_json(input_file: str, output_file: str):
    """
    Otimiza o JSON:
    - Remove campos não usados (createdAt, updatedAt, SequelizeMeta)
    - Comprime nomes de chaves
    - Minifica (sem espaços)
    """
    print(f"Carregando {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_size = get_file_size_mb(input_file)
    print(f"Tamanho original: {original_size:.2f} MB\n")

    # Mapeia nomes longos para curtos
    key_map = {
        'image_url': 'img',
        'logo_url': 'logo',
        'team_id': 'tid',
        'game_id': 'gid',
        'pro_settings': 'ps',
        'country': 'co',
    }

    # Campos para remover (não usados no frontend)
    fields_to_remove = {'createdAt', 'updatedAt', 'SequelizeMeta'}

    def compress_keys(obj):
        """Recursivamente comprime nomes de chaves e remove campos desnecessários."""
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

    # Remove SequelizeMeta
    data = {k: v for k, v in data.items() if k not in fields_to_remove}

    print("Processando otimizações...")
    print("  ✓ Removendo campos não usados (createdAt, updatedAt)")
    print("  ✓ Comprimindo nomes de chaves")
    print("  ✓ Minificando JSON\n")

    # Comprime os dados
    optimized_data = compress_keys(data)

    # Salva minificado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, separators=(',', ':'))

    optimized_size = get_file_size_mb(output_file)

    # Resumo
    print("=" * 50)
    print("RESUMO")
    print("=" * 50)
    print(f"Arquivo original:   {original_size:.2f} MB")
    print(f"Arquivo otimizado:  {optimized_size:.2f} MB")
    print(f"Redução:            {original_size - optimized_size:.2f} MB ({((original_size - optimized_size) / original_size * 100):.1f}%)")
    print(f"\nArquivo salvo em:   {output_file}")

    # Mostra estatísticas
    print(f"\n" + "=" * 50)
    print("ESTATÍSTICAS")
    print("=" * 50)
    for table_name, records in optimized_data.items():
        print(f"{table_name}: {len(records)} registros")

    print(f"\n" + "=" * 50)
    print("MAPEAMENTO DE CHAVES")
    print("=" * 50)
    for original, compressed in key_map.items():
        print(f"{original:20} → {compressed}")


if __name__ == "__main__":
    optimize_json("prosettings_data.json", "prosettings_optimized.json")

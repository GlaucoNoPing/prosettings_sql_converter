#!/usr/bin/env python3
"""
Valida e conta dados diretamente do arquivo SQL.
Mostra quantidade de jogos e players por jogo.
"""

import re
from collections import defaultdict


def count_from_sql(sql_file: str):
    """
    Lê o arquivo SQL e conta:
    - Quantidade de games
    - Quantidade de players por game
    """
    print(f"Lendo arquivo SQL: {sql_file}")
    print("=" * 70)

    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai INSERT statements
    insert_pattern = r"INSERT\s+INTO\s+`(\w+)`\s*\("
    matches = list(re.finditer(insert_pattern, content, re.IGNORECASE))

    # Processa cada INSERT
    tables_data = {}

    for i, match in enumerate(matches):
        table_name = match.group(1)
        start_pos = match.end()

        # Extrai colunas
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

        # Procura VALUES
        values_match = re.search(r"\s*VALUES\s+", content[col_end:col_end+50], re.IGNORECASE)
        if not values_match:
            continue

        values_start = col_end + values_match.end()

        # Procura fim do INSERT (;)
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

        # Conta registros (cada registro começa com '(')
        # Precisamos contar apenas parênteses que não estão dentro de strings
        record_count = 0
        in_str = False
        esc = False

        for char in values_section:
            if esc:
                esc = False
                continue
            if char == '\\':
                esc = True
                continue
            if char == "'":
                in_str = not in_str
            if char == '(' and not in_str:
                record_count += 1

        if table_name not in tables_data:
            tables_data[table_name] = {
                'columns': columns,
                'count': 0
            }

        tables_data[table_name]['count'] += record_count

    # Mostra resultados
    print("\n📊 CONTAGEM DE REGISTROS NO SQL")
    print("=" * 70)

    for table_name, data in sorted(tables_data.items()):
        print(f"{table_name:25} {data['count']:6,} registros")

    # Análise específica para games e game_player
    print("\n" + "=" * 70)
    print("🎮 ANÁLISE DETALHADA")
    print("=" * 70)

    games_count = tables_data.get('games', {}).get('count', 0)
    players_count = tables_data.get('players', {}).get('count', 0)
    game_player_count = tables_data.get('game_player', {}).get('count', 0)
    settings_count = tables_data.get('settings', {}).get('count', 0)

    print(f"\nTotal de Games: {games_count}")
    print(f"Total de Players: {players_count}")
    print(f"Total de Relacionamentos game_player: {game_player_count:,}")
    print(f"Total de Settings: {settings_count:,}")

    # Extrai dados específicos para contar players por game
    # Precisamos parsear o conteúdo de game_player
    print("\n" + "=" * 70)
    print("👥 PLAYERS POR GAME (via game_player)")
    print("=" * 70)

    # Encontra o INSERT de game_player
    game_player_pattern = r"INSERT\s+INTO\s+`game_player`.*?VALUES\s+(.*?);"
    gp_match = re.search(game_player_pattern, content, re.IGNORECASE | re.DOTALL)

    if gp_match:
        gp_values = gp_match.group(1)

        # Parse valores - formato: ('id', 'game_id', 'player_id', ...)
        # Procura padrão de UUIDs
        row_pattern = r"\('([a-f0-9\-]+)',\s*'([a-f0-9\-]+)',\s*'([a-f0-9\-]+)'"

        game_player_counts = defaultdict(int)

        for match in re.finditer(row_pattern, gp_values):
            # match.group(1) = id (não usado)
            game_id = match.group(2)  # game_id
            # player_id = match.group(3)  # player_id (não usado aqui)

            game_player_counts[game_id] += 1

        # Extrai nomes dos games
        games_pattern = r"INSERT\s+INTO\s+`games`.*?VALUES\s+(.*?);"
        games_match = re.search(games_pattern, content, re.IGNORECASE | re.DOTALL)

        game_names = {}
        if games_match:
            games_values = games_match.group(1)
            # Parse: ('id', 'name', ...)
            game_row_pattern = r"\('([a-f0-9\-]+)',\s*'([^']+)'"

            for match in re.finditer(game_row_pattern, games_values):
                game_id = match.group(1)
                game_name = match.group(2)
                game_names[game_id] = game_name

        # Mostra contagem por game
        print(f"\n{'Game':<30} {'Players':<10}")
        print("-" * 45)

        total_players = 0
        for game_id, count in sorted(game_player_counts.items(), key=lambda x: x[1], reverse=True):
            game_name = game_names.get(game_id, f"Unknown ({game_id[:8]})")
            print(f"{game_name:<30} {count:>6,}")
            total_players += count

        print("-" * 45)
        print(f"{'TOTAL':<30} {total_players:>6,}")

    print("\n" + "=" * 70)
    print("✅ Validação SQL concluída")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    sql_file = "bdprosettingscorreto.sql"

    if len(sys.argv) > 1:
        sql_file = sys.argv[1]

    count_from_sql(sql_file)

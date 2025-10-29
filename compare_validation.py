#!/usr/bin/env python3
"""
Compara os resultados da validação SQL vs JSON.
Mostra diferenças e verifica integridade dos dados.
"""

import re
import json
from collections import defaultdict


def extract_sql_data(sql_file: str):
    """Extrai dados do SQL."""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai game_player
    game_player_pattern = r"INSERT\s+INTO\s+`game_player`.*?VALUES\s+(.*?);"
    gp_match = re.search(game_player_pattern, content, re.IGNORECASE | re.DOTALL)

    game_player_counts = defaultdict(int)
    if gp_match:
        gp_values = gp_match.group(1)
        row_pattern = r"\('([a-f0-9\-]+)',\s*'([a-f0-9\-]+)',\s*'([a-f0-9\-]+)'"
        for match in re.finditer(row_pattern, gp_values):
            game_id = match.group(2)
            game_player_counts[game_id] += 1

    # Extrai nomes dos games
    games_pattern = r"INSERT\s+INTO\s+`games`.*?VALUES\s+(.*?);"
    games_match = re.search(games_pattern, content, re.IGNORECASE | re.DOTALL)

    game_names = {}
    if games_match:
        games_values = games_match.group(1)
        game_row_pattern = r"\('([a-f0-9\-]+)',\s*'([^']+)'"
        for match in re.finditer(game_row_pattern, games_values):
            game_id = match.group(1)
            game_name = match.group(2)
            game_names[game_id] = game_name

    # Conta settings
    settings_pattern = r"INSERT\s+INTO\s+`settings`"
    settings_count = 0
    for match in re.finditer(settings_pattern, content, re.IGNORECASE):
        settings_count += 1

    return {
        'games': len(game_names),
        'players_total': sum(game_player_counts.values()),
        'game_player_counts': {game_names.get(gid, gid): count for gid, count in game_player_counts.items()},
        'settings_inserts': settings_count
    }


def extract_json_data(json_file: str):
    """Extrai dados do JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    games = data.get('games', [])

    game_player_counts = {}
    total_players = 0
    total_settings = 0

    for game in games:
        game_name = game.get('name', 'Unknown')
        player_count = len(game.get('players', []))
        game_player_counts[game_name] = player_count
        total_players += player_count

        for player in game.get('players', []):
            if 'settings' in player:
                total_settings += len(player['settings'])

    return {
        'games': len(games),
        'players_total': total_players,
        'game_player_counts': game_player_counts,
        'settings_total': total_settings
    }


def compare_data(sql_file: str, json_file: str):
    """Compara dados do SQL e JSON."""
    print("=" * 70)
    print("COMPARAÇÃO: SQL vs JSON")
    print("=" * 70)

    sql_data = extract_sql_data(sql_file)
    json_data = extract_json_data(json_file)

    # Comparação geral
    print("\n📊 TOTAIS")
    print("-" * 70)
    print(f"{'Métrica':<30} {'SQL':>15} {'JSON':>15} {'Match':>8}")
    print("-" * 70)

    games_match = "✅" if sql_data['games'] == json_data['games'] else "❌"
    players_match = "✅" if sql_data['players_total'] == json_data['players_total'] else "❌"

    print(f"{'Games':<30} {sql_data['games']:>15,} {json_data['games']:>15,} {games_match:>8}")
    print(f"{'Players (total)':<30} {sql_data['players_total']:>15,} {json_data['players_total']:>15,} {players_match:>8}")

    # Comparação por game
    print("\n" + "=" * 70)
    print("👥 PLAYERS POR GAME")
    print("-" * 70)
    print(f"{'Game':<30} {'SQL':>15} {'JSON':>15} {'Match':>8}")
    print("-" * 70)

    all_games = set(sql_data['game_player_counts'].keys()) | set(json_data['game_player_counts'].keys())

    all_match = True
    for game_name in sorted(all_games, key=lambda g: sql_data['game_player_counts'].get(g, 0), reverse=True):
        sql_count = sql_data['game_player_counts'].get(game_name, 0)
        json_count = json_data['game_player_counts'].get(game_name, 0)
        match = "✅" if sql_count == json_count else "❌"

        if sql_count != json_count:
            all_match = False

        print(f"{game_name:<30} {sql_count:>15,} {json_count:>15,} {match:>8}")

    # Resultado final
    print("\n" + "=" * 70)
    print("RESULTADO DA VALIDAÇÃO")
    print("=" * 70)

    if all_match and games_match == "✅" and players_match == "✅":
        print("\n✅ TODOS OS DADOS BATEM PERFEITAMENTE!")
        print("   Nenhum dado foi perdido na conversão SQL → JSON")
    else:
        print("\n⚠️  ATENÇÃO: Existem diferenças entre SQL e JSON")
        print("   Verifique os dados acima para identificar discrepâncias")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys

    sql_file = "bdprosettingscorreto.sql"
    json_file = "prosettings.json"

    if len(sys.argv) > 1:
        sql_file = sys.argv[1]

    if len(sys.argv) > 2:
        json_file = sys.argv[2]

    compare_data(sql_file, json_file)

#!/usr/bin/env python3
"""
Valida e conta dados diretamente do arquivo JSON.
Mostra quantidade de jogos e players por jogo.
"""

import json


def count_from_json(json_file: str):
    """
    Lê o arquivo JSON e conta:
    - Quantidade de games
    - Quantidade de players por game
    """
    print(f"Lendo arquivo JSON: {json_file}")
    print("=" * 70)

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    games = data.get('games', [])

    print("\n📊 CONTAGEM DE REGISTROS NO JSON")
    print("=" * 70)

    total_games = len(games)
    total_players = 0
    total_settings = 0

    print(f"{'Tabela':<25} {'Registros':>10}")
    print("-" * 40)
    print(f"{'games':<25} {total_games:>10,}")

    # Conta players e settings
    for game in games:
        players_in_game = game.get('players', [])
        total_players += len(players_in_game)

        for player in players_in_game:
            if 'settings' in player:
                # Conta cada tipo de setting
                total_settings += len(player['settings'])

    print(f"{'players (total)':<25} {total_players:>10,}")
    print(f"{'settings (total)':<25} {total_settings:>10,}")

    # Análise detalhada
    print("\n" + "=" * 70)
    print("🎮 ANÁLISE DETALHADA")
    print("=" * 70)

    print(f"\nTotal de Games: {total_games}")
    print(f"Total de Players (únicos): {total_players:,}")
    print(f"Total de Settings (configurações): {total_settings:,}")

    # Players por game
    print("\n" + "=" * 70)
    print("👥 PLAYERS POR GAME")
    print("=" * 70)

    print(f"\n{'Game':<30} {'Players':<10}")
    print("-" * 45)

    # Ordena por quantidade de players (maior primeiro)
    games_sorted = sorted(games, key=lambda g: len(g.get('players', [])), reverse=True)

    total_counted = 0
    for game in games_sorted:
        game_name = game.get('name', 'Unknown')
        player_count = len(game.get('players', []))
        print(f"{game_name:<30} {player_count:>6,}")
        total_counted += player_count

    print("-" * 45)
    print(f"{'TOTAL':<30} {total_counted:>6,}")

    # Estatísticas de settings
    print("\n" + "=" * 70)
    print("⚙️ ESTATÍSTICAS DE SETTINGS")
    print("=" * 70)

    settings_types = {}
    players_with_settings = 0

    for game in games:
        for player in game.get('players', []):
            if 'settings' in player and player['settings']:
                players_with_settings += 1
                for setting_name in player['settings'].keys():
                    settings_types[setting_name] = settings_types.get(setting_name, 0) + 1

    print(f"\nPlayers com settings: {players_with_settings:,} de {total_players:,}")
    print(f"Tipos de settings diferentes: {len(settings_types)}")

    if settings_types:
        print(f"\n{'Tipo de Setting':<35} {'Quantidade':<10}")
        print("-" * 50)
        for setting_name, count in sorted(settings_types.items(), key=lambda x: x[1], reverse=True):
            print(f"{setting_name:<35} {count:>6,}")

    print("\n" + "=" * 70)
    print("✅ Validação JSON concluída")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    json_file = "prosettings.json"

    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    count_from_json(json_file)

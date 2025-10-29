# ProSettings SQL to JSON Converter

Conversor de dados SQL para JSON otimizado. Extrai dados de um arquivo SQL dump e gera um arquivo JSON sem duplicação de dados, perfeito para manter em memória.

## 📦 Arquivo Final

```
prosettings_sql_converter/
├── sql_to_json.py              # Script de conversão SQL → JSON
├── prosettings.json            # JSON otimizado (2.0 MB) ⭐
├── bdprosettingscorreto.sql    # Arquivo SQL de entrada
├── requirements.txt            # Dependências (apenas stdlib)
└── README.md                   # Este arquivo
```

## 📊 Dados Inclusos

- **Games:** 11 jogos
- **Players:** 1.777 jogadores distribuídos entre os games
- **Settings:** Configurações completas por player/game

### Distribuição de Players por Game

| Game | Players |
|------|---------|
| CS2 | 842 |
| Valorant | 506 |
| Fortnite | 294 |
| Apex Legends | 82 |
| Overwatch 2 | 61 |
| PUBG | 48 |
| Rainbow Six Siege | 21 |
| League of Legends | 20 |
| Call of Duty: Warzone | 13 |
| Deadlock | 9 |
| Dota 2 | 0 |

## 🚀 Como Usar

```python
import json

# Carregar JSON em memória
with open('prosettings.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Acessar dados
games = data['games']

# Exemplo 1: Buscar um game específico
cs2 = next(g for g in games if g['name'] == 'CS2')
print(f"CS2 tem {len(cs2['players'])} players")

# Exemplo 2: Buscar um player específico dentro de um game
valorant = next(g for g in games if g['name'] == 'Valorant')
tenz = next(p for p in valorant['players'] if p['name'] == 'tenz')

# Exemplo 3: Acessar settings do player
mouse_settings = tenz['settings']['mouse_settings']
print(f"DPI: {mouse_settings['dpi']}")
```

## 📋 Estrutura do JSON

```json
{
  "games": [
    {
      "id": "uuid",
      "name": "Valorant",
      "img": "uuid.png",
      "players": [
        {
          "id": "uuid",
          "name": "tenz",
          "team": "Sentinels",
          "img": "uuid.png",
          "link": "https://prosettings.net/players/tenz/",
          "settings": {
            "mouse_settings": {
              "dpi": "800",
              "sensitivity": "0.35",
              "hz": "1000"
            },
            "crosshair_settings": { ... },
            "video_settings": { ... }
          }
        }
      ]
    }
  ]
}
```

## ✅ Vantagens da Estrutura

**Antes (formato relacional):**
- ❌ 3.43 MB
- ❌ UUIDs duplicados (gid, pid) em 8.519 settings
- ❌ Tabela game_player separada com 1.896 relacionamentos
- ❌ Dados dos games duplicados se colocados dentro de cada player
- ❌ Difícil de usar (precisa fazer joins no frontend)

**Agora (formato otimizado):**
- ✅ 2.00 MB (redução de 41.7%)
- ✅ Sem duplicação de UUIDs
- ✅ Cada game aparece apenas 1 vez
- ✅ Estrutura lógica: games → players → settings
- ✅ Acesso direto: `game.players[0].settings`
- ✅ Perfeito para manter em memória

## 🔄 Gerar JSON a partir de um SQL

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Converter SQL para JSON
python sql_to_json.py seu_arquivo.sql output.json

# Desativar ambiente
deactivate
```

## ⚙️ Tecnologias

- Python 3.7+
- Bibliotecas padrão: `re`, `json`, `typing`, `os`
- Sem dependências externas

## 💡 Por que Games → Players?

A estrutura `games → players → settings` foi escolhida porque:

1. **Evita duplicação de games**: Se colocássemos players primeiro, os dados de cada game (id, name, img) seriam duplicados para cada player que joga aquele game
2. **Organização lógica**: É mais natural buscar "quais players jogam CS2" do que "quais games o player joga"
3. **Redução de tamanho**: Menos duplicação = arquivo menor
4. **Fácil de usar**: `cs2.players` é intuitivo e direto

## 📝 Notas

- JSON otimizado para manter em memória (2.0 MB)
- UUIDs preservados para referência de imagens
- CS2 é o game com mais players (842)
- Valorant em segundo lugar (506 players)

# ProSettings SQL to JSON Converter

Conversor de dados SQL para JSON do banco de dados ProSettings. Este projeto extrai dados de um arquivo SQL dump e os converte para um formato JSON otimizado.

## 📊 Resultados da Conversão

O script processa com sucesso:
- **10 jogos** (CS2, Valorant, Fortnite, etc.)
- **1.734 jogadores profissionais** com suas configurações detalhadas
- **523 equipes**
- Configurações JSON aninhadas preservadas (mouse, crosshair, viewmodel)

## 📦 Estrutura do Projeto

```
prosettings_sql_converter/
├── .venv/                       # Ambiente virtual Python
├── .gitignore                   # Arquivos ignorados pelo Git
├── sql_to_json.py              # Script de conversão SQL → JSON
├── optimize_single_json.py     # Script de otimização do JSON
├── requirements.txt            # Dependências (nenhuma externa)
├── prosettings_data.json       # JSON completo (2.27 MB)
├── prosettings_optimized.json  # JSON otimizado (1.34 MB) ✨
└── README.md                   # Este arquivo
```

## 🚀 Como Usar

### Passo 1: Ativar o ambiente virtual

```bash
source .venv/bin/activate
```

### Passo 2: Converter SQL para JSON

```bash
# Gera prosettings_data.json (2.27 MB)
python sql_to_json.py
```

### Passo 3: Otimizar o JSON (RECOMENDADO)

```bash
# Gera prosettings_optimized.json (1.34 MB)
python optimize_single_json.py
```

### Desativar ambiente virtual

```bash
deactivate
```

## 📉 Otimizações Aplicadas

### Redução de Tamanho

| Versão | Tamanho | Redução |
|--------|---------|---------|
| Original | 2.27 MB | - |
| Otimizado | 1.34 MB | **40.7%** |

### O que foi otimizado?

✅ **Remoção de campos não usados**
- `createdAt` removido
- `updatedAt` removido
- `SequelizeMeta` removido

✅ **Compressão de nomes de chaves**
- `country` → `co`
- `image_url` → `img`
- `logo_url` → `logo`
- `team_id` → `tid`
- `game_id` → `gid`
- `pro_settings` → `ps`

✅ **Minificação**
- Sem espaços ou quebras de linha
- Separadores compactos

## 📋 Estrutura do JSON Otimizado

```json
{
  "games": [
    {
      "id": 11,
      "name": "CS2",
      "logo": "CS2-2024-08-29T01-34-47-989Z.png"
    }
  ],
  "teams": [
    {
      "id": 527,
      "name": "G2 Esports",
      "logo": "G2 Esports-2024-08-29T01-34-48-257Z.png"
    }
  ],
  "players": [
    {
      "id": 60,
      "name": "tenz",
      "co": "Canada",
      "img": "tenz-2024-08-29T01-46-17-357Z.png",
      "tid": 898,
      "gid": 12,
      "ps": {
        "mouse": {...},
        "crosshair": {...},
        "viewmodel": {...}
      }
    }
  ]
}
```

## 🗺️ Mapeamento de Chaves

Use este mapeamento ao acessar os dados no frontend:

| Chave Original | Chave Comprimida |
|----------------|------------------|
| country | co |
| image_url | img |
| logo_url | logo |
| team_id | tid |
| game_id | gid |
| pro_settings | ps |

**Exemplo de uso:**
```javascript
// Acessar dados com chaves comprimidas
player.name        // nome do player
player.co          // country
player.img         // image_url
player.tid         // team_id
player.gid         // game_id
player.ps          // pro_settings (objeto com mouse, crosshair, viewmodel)
```

## 🛠️ Scripts Disponíveis

1. **sql_to_json.py** - Converte SQL dump para JSON
2. **optimize_single_json.py** - Otimiza o JSON gerado

## 📊 Estatísticas

- **Games:** 10 registros
- **Players:** 1.734 registros
- **Teams:** 523 registros
- **Redução:** 40.7% (de 2.27 MB para 1.34 MB)

## ⚙️ Funcionalidades

- Extração automática de todas as tabelas do SQL
- Preservação de tipos de dados (strings, números, JSON, NULL)
- Parsing correto de dados JSON aninhados (como `pro_settings`)
- Suporte para caracteres UTF-8
- Compressão de nomes de chaves
- Remoção de campos não utilizados
- Minificação do JSON

## 🔧 Tecnologias

- Python 3.7+
- Bibliotecas padrão: `re`, `json`, `typing`, `os`
- Sem dependências externas

## 📝 Notas

- Use **prosettings_optimized.json** em produção (1.34 MB)
- Mantenha o mapeamento de chaves documentado
- O arquivo original (prosettings_data.json) pode ser usado para referência

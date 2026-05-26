# 🏠 HA Smart Home UI

Dashboard Lovelace para Home Assistant inspirado no design **Smart Home** (estilo Tuya/cream+plum+orange).

## Telas (9 views)

| # | Arquivo | Descrição |
|---|---------|-----------|
| 01 | `dashboards/01-dashboard.yaml` | Dashboard principal — saudação, cena ativa, grid de dispositivos |
| 02 | `dashboards/02-luz.yaml` | Controle de luz — brilho, temperatura de cor, presets |
| 03 | `dashboards/03-clima.yaml` | Climatização — termostato, modos, velocidade do ventilador |
| 04 | `dashboards/04-cenas.yaml` | Cenas & Rotinas — galeria de cenas e ativação |
| 05 | `dashboards/05-energia.yaml` | Energia — consumo, gráficos, maiores consumidores |
| 06 | `dashboards/06-acessos.yaml` | Acessos — cortinas, janelas, portas/fechaduras |
| 07 | `dashboards/07-sensores.yaml` | Sensores — temperatura, umidade, lux, movimento, ocupação |
| 08 | `dashboards/08-voz.yaml` | Assistente de voz — Alexa / HA Voice |
| 09 | `dashboards/09-cozinha.yaml` | Cozinha — eletrodomésticos inteligentes |

`full_dashboard.yaml` contém **todas as 9 telas num único arquivo** para colar no HA.

## Requisitos

### Custom Cards (instalar via HACS)

```
button-card         — cartões de dispositivo estilizados
mini-graph-card     — gráficos mini
card-mod            — CSS customizado nos cards
mushroom            — cards modernos (opcional, alternativo)
```

### Tema

Copie `themes/smart-home-theme.yaml` para o diretório `themes/` do HA e adicione em `configuration.yaml`:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

Ative em: Perfil > Tema > **Smart Home Cream**

## Como usar

### Opção A — Dashboard completo
1. Vá em **Configurações > Painéis > Adicionar painel**
2. Escolha **Lovelace YAML**
3. Cole o conteúdo de `full_dashboard.yaml`
4. Substitua os `entity_id` pelos seus (veja tabela abaixo)

### Opção B — Vista por vista
1. Abra um painel existente > três pontos > **Editar** > **YAML bruto**
2. Cole o conteúdo de cada `dashboards/0X-*.yaml` como uma nova entrada em `views:`

## Gerador de cartões (Python CLI)

```bash
cd generator/
python generate_card.py --entity light.sala_pendente_norte
python generate_card.py --entity switch.tomada_tv --style dark
python generate_card.py --entity climate.sala_ac --output clima_card.yaml
python generate_card.py --entity cover.cortinas_sala
python generate_card.py --entity sensor.temperatura_sala
python generate_card.py --entity media_player.sala
```

**Tipos suportados:** `light`, `switch`, `climate`, `cover`, `lock`, `sensor`, `binary_sensor`, `scene`, `script`, `media_player`, `input_boolean`, `fan`

## Substituição de Entidades

Adapte os `entity_id` às suas entidades reais:

| Placeholder | Sua entidade |
|-------------|-------------|
| `light.sala_pendente_norte` | Sua luminária da sala |
| `light.sala_fita_led` | Sua fita LED |
| `climate.sala_ac` | Seu ar-condicionado |
| `cover.sala_cortinas` | Suas cortinas |
| `lock.porta_entrada` | Sua fechadura inteligente |
| `sensor.sala_temperatura` | Sensor de temperatura |
| `sensor.sala_umidade` | Sensor de umidade |
| `sensor.sala_luminosidade` | Sensor de lux |
| `binary_sensor.sala_movimento` | Sensor de movimento |
| `media_player.sala` | Caixa de som / Alexa |

## Paleta de cores (design tokens)

```
bgCream   #EFE7D8   Fundo principal (cream quente)
plum      #2E2742   Roxo profundo (cards escuros, nav)
orange    #F08648   Laranja (acento, botões ativos)
mint      #BFDDC4   Menta (sensores, estados positivos)
lavender  #D2C5E6   Lavanda (clima, automações)
blush     #F1DCD4   Rosa suave (temperatura, frio)
peach     #F6B584   Pêssego (blobs de fundo)
```

## Licença

MIT — Maycon Willian Oliveira

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HA Smart Home UI — Gerador de Cartões Lovelace                             ║
║  Design: Smart Home (estilo cream/plum/orange)                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Uso:
    python generate_card.py --entity light.sala_pendente_norte
    python generate_card.py --entity climate.sala_ac --style dark
    python generate_card.py --entity cover.cortinas_sala --output card.yaml
    python generate_card.py --entity sensor.temperatura_sala --style minimal
    python generate_card.py --entity media_player.sala
    python generate_card.py --list-types

Tipos suportados:
    light, switch, climate, cover, lock, sensor, binary_sensor,
    scene, script, media_player, input_boolean, fan, vacuum
"""

import argparse
import sys
import textwrap
from pathlib import Path

# ── Paleta de Cores (Smart Home Design Tokens) ────────────────────────────────
TOKENS = {
    "bgCream":    "#EFE7D8",
    "bgWarm":     "#E9DFCB",
    "bgPaper":    "#F5EFE2",
    "plum":       "#2E2742",
    "plumSoft":   "#3D3654",
    "ink":        "#1E1830",
    "orange":     "#F08648",
    "orangeDeep": "#E36A2A",
    "peach":      "#F6B584",
    "mint":       "#BFDDC4",
    "mintDeep":   "#7FB892",
    "lavender":   "#D2C5E6",
    "lavDeep":    "#9E8AC4",
    "blush":      "#F1DCD4",
    "blushDeep":  "#E5B7AC",
    "card":       "#FFFFFF",
    "cardSoft":   "#FBF6EC",
    "text":       "#2E2742",
    "textMute":   "#7A7388",
    "textFaint":  "#B6B0C2",
    "shadowSoft": "0 8px 24px rgba(46,39,66,0.08), 0 2px 6px rgba(46,39,66,0.04)",
    "shadowCard": "0 16px 40px rgba(46,39,66,0.10), 0 4px 12px rgba(46,39,66,0.06)",
    "shadowDark": "0 18px 40px rgba(20,15,35,0.35)",
}

# ── Mapeamento: domínio → ícone MDI padrão ─────────────────────────────────
ICON_MAP = {
    "light":          "mdi:lightbulb",
    "switch":         "mdi:toggle-switch",
    "climate":        "mdi:thermostat",
    "cover":          "mdi:blinds",
    "lock":           "mdi:lock",
    "sensor":         "mdi:eye",
    "binary_sensor":  "mdi:motion-sensor",
    "scene":          "mdi:palette",
    "script":         "mdi:script-text",
    "media_player":   "mdi:speaker",
    "input_boolean":  "mdi:toggle-switch-off",
    "fan":            "mdi:fan",
    "vacuum":         "mdi:robot-vacuum",
    "input_number":   "mdi:numeric",
    "input_select":   "mdi:form-select",
    "automation":     "mdi:robot-outline",
    "button":         "mdi:gesture-tap-button",
}

# ── Mapeamento: keyword no entity_id → ícone especializado ────────────────
ICON_KEYWORDS = {
    "temperatura": "mdi:thermometer",
    "umidade":     "mdi:water-percent",
    "luminosidade": "mdi:brightness-5",
    "lux":         "mdi:brightness-5",
    "movimento":   "mdi:motion-sensor",
    "presenca":    "mdi:account-check",
    "ocupacao":    "mdi:account-group",
    "co2":         "mdi:molecule-co2",
    "cortinas":    "mdi:curtains",
    "persianas":   "mdi:blinds",
    "janela":      "mdi:window-open",
    "porta":       "mdi:door",
    "garagem":     "mdi:garage",
    "tv":          "mdi:television",
    "geladeira":   "mdi:fridge-outline",
    "microondas":  "mdi:microwave",
    "cafeteira":   "mdi:coffee-maker",
    "airfryer":    "mdi:pot-steam-outline",
    "panela":      "mdi:pot-outline",
    "sanduicheira":"mdi:toaster-oven",
    "liquidificador": "mdi:blender-outline",
    "exaustor":    "mdi:fan",
    "ventilador":  "mdi:fan",
    "ar_cond":     "mdi:air-conditioner",
    "ac":          "mdi:air-conditioner",
    "climatizador":"mdi:air-conditioner",
    "umidificador":"mdi:air-humidifier",
    "purificador": "mdi:air-purifier",
    "escova":      "mdi:tooth-outline",
    "fita_led":    "mdi:led-strip-variant",
    "led":         "mdi:led-strip-variant",
    "pendente":    "mdi:ceiling-light",
    "teto":        "mdi:ceiling-light",
    "arandela":    "mdi:wall-sconce",
    "abajur":      "mdi:lamp",
    "alexa":       "mdi:amazon-alexa",
    "speaker":     "mdi:speaker",
    "musica":      "mdi:music",
    "tomada":      "mdi:power-plug",
    "chuveiro":    "mdi:shower-head",
}

# ── Mapeamento: keyword → cor de tint ─────────────────────────────────────
TINT_MAP = {
    "temperatura":  TOKENS["blush"],
    "umidade":      TOKENS["mint"],
    "luminosidade": TOKENS["peach"],
    "lux":          TOKENS["peach"],
    "movimento":    TOKENS["lavender"],
    "presenca":     TOKENS["lavender"],
    "tv":           TOKENS["blush"],
    "geladeira":    TOKENS["lavender"],
    "cafeteira":    TOKENS["peach"],
    "airfryer":     TOKENS["peach"],
    "liquidificador": TOKENS["mint"],
    "exaustor":     TOKENS["lavender"],
    "ventilador":   TOKENS["mint"],
    "ar_cond":      TOKENS["lavender"],
    "ac":           TOKENS["lavender"],
    "climatizador": TOKENS["lavender"],
    "umidificador": TOKENS["mint"],
    "purificador":  TOKENS["lavender"],
    "led":          TOKENS["peach"],
    "fita_led":     TOKENS["peach"],
}


def infer_icon(entity_id: str, domain: str) -> str:
    """Infere ícone MDI com base no entity_id e domínio."""
    slug = entity_id.split(".")[-1].lower()
    for keyword, icon in ICON_KEYWORDS.items():
        if keyword in slug:
            return icon
    return ICON_MAP.get(domain, "mdi:help-circle")


def infer_tint(entity_id: str, default: str = TOKENS["peach"]) -> str:
    """Infere cor de tint com base no entity_id."""
    slug = entity_id.split(".")[-1].lower()
    for keyword, color in TINT_MAP.items():
        if keyword in slug:
            return color
    return default


def infer_name(entity_id: str) -> str:
    """Gera um nome legível a partir do entity_id."""
    slug = entity_id.split(".")[-1]
    return slug.replace("_", " ").title()


def generate_light_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade light."""
    name = infer_name(entity_id)
    icon = infer_icon(entity_id, "light")
    tint = infer_tint(entity_id, TOKENS["peach"])

    if style == "dark":
        bg_on, bg_off = "rgba(255,255,255,0.12)", "rgba(255,255,255,0.06)"
        text_color = "#FFFFFF"
        shadow = "none"
    else:
        bg_on, bg_off = TOKENS["card"], TOKENS["cardSoft"]
        text_color = TOKENS["text"]
        shadow = TOKENS["shadowSoft"]

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Iluminação
# Custom cards necessários: button-card
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: >-
  [[[ const b = entity.attributes.brightness;
      return entity.state === 'on'
        ? (b ? Math.round(b/2.55) + '% · Ligada' : 'Ligada')
        : 'Desligado'; ]]]
show_label: true
icon: {icon}
tap_action:
  action: toggle
hold_action:
  action: more-info
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '{bg_on}' : '{bg_off}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{shadow}"
    - min-height: "120px"
    - transition: "all 0.25s"
  icon:
    - color: "[[[ return entity.state === 'on' ? '{TOKENS['text']}' : '{TOKENS['textMute']}' ]]]"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'on' ? '{tint}' : 'rgba(46,39,66,0.06)' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{text_color}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


def generate_switch_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade switch."""
    name = infer_name(entity_id)
    icon = infer_icon(entity_id, "switch")
    tint = infer_tint(entity_id, TOKENS["lavender"])

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Interruptor / Tomada Inteligente
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: "[[[ return entity.state === 'on' ? 'Ligado' : 'Desligado' ]]]"
show_label: true
icon: {icon}
tap_action:
  action: toggle
hold_action:
  action: more-info
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '{TOKENS['card']}' : '{TOKENS['cardSoft']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
    - transition: "all 0.25s"
  icon:
    - color: "[[[ return entity.state === 'on' ? '{TOKENS['plum']}' : '{TOKENS['textMute']}' ]]]"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'on' ? '{tint}' : 'rgba(46,39,66,0.06)' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


def generate_climate_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade climate."""
    name = infer_name(entity_id)

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Climatização (Ar-condicionado / Aquecedor / Termostato)
# Dica: use card_mod para ajustar cores do termostato nativo
type: thermostat
entity: {entity_id}
card_mod:
  style: |
    ha-card {{
      background: {TOKENS['card']} !important;
      border-radius: 32px !important;
      box-shadow: {TOKENS['shadowCard']} !important;
    }}
    round-slider {{
      --round-slider-path-color: rgba(46,39,66,0.1);
      --round-slider-bar-color: {TOKENS['orange']};
    }}

---
# Alternativa: button-card para controle rápido de modo
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: >-
  [[[ const mode = entity.attributes.hvac_mode;
      const temp = entity.attributes.temperature;
      return (temp ? temp + '° · ' : '') + (mode || ''); ]]]
show_label: true
icon: mdi:thermostat
tap_action:
  action: more-info
styles:
  card:
    - background: "[[[ return entity.state !== 'off' ? '{TOKENS['card']}' : '{TOKENS['cardSoft']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
  icon:
    - color: "[[[ return entity.state !== 'off' ? '{TOKENS['lavDeep']}' : '{TOKENS['textMute']}' ]]]"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state !== 'off' ? '{TOKENS['lavender']}' : 'rgba(46,39,66,0.06)' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


def generate_cover_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade cover (cortinas, persianas, janelas)."""
    name = infer_name(entity_id)
    icon = infer_icon(entity_id, "cover")

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Abertura (Cortinas / Persianas / Janela / Portão)
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: >-
  [[[ const pos = entity.attributes.current_position;
      if (pos === undefined) return entity.state;
      return pos > 0 ? `Aberta ${{pos}}%` : 'Fechada'; ]]]
show_label: true
icon: {icon}
tap_action:
  action: more-info
hold_action:
  action: call-service
  service: cover.toggle
  target:
    entity_id: {entity_id}
styles:
  card:
    - background: "{TOKENS['card']}"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
  icon:
    - color: "{TOKENS['mintDeep']}"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "{TOKENS['mint']}"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"

# ── Controles rápidos (abrir / parar / fechar) ───────────────────────
# Adicione abaixo do card acima em um horizontal-stack:
#
# - type: horizontal-stack
#   cards:
#     - type: custom:button-card
#       name: "Fechar"
#       icon: mdi:arrow-down
#       tap_action:
#         action: call-service
#         service: cover.close_cover
#         target:
#           entity_id: {entity_id}
#       styles:
#         card:
#           - background: "{TOKENS['plum']}"
#           - border-radius: "999px"
#           - padding: "12px 0"
#         name:
#           - color: "#FFFFFF"
#           - font-size: "12px"
#           - font-weight: "700"
#     - type: custom:button-card
#       name: "Parar"
#       icon: mdi:stop
#       tap_action:
#         action: call-service
#         service: cover.stop_cover
#         target:
#           entity_id: {entity_id}
#       styles:
#         card:
#           - background: "{TOKENS['bgWarm']}"
#           - border-radius: "999px"
#           - padding: "12px 0"
#         name:
#           - color: "{TOKENS['plum']}"
#           - font-size: "12px"
#           - font-weight: "700"
#     - type: custom:button-card
#       name: "Abrir"
#       icon: mdi:arrow-up
#       tap_action:
#         action: call-service
#         service: cover.open_cover
#         target:
#           entity_id: {entity_id}
#       styles:
#         card:
#           - background: "{TOKENS['orange']}"
#           - border-radius: "999px"
#           - padding: "12px 0"
#         name:
#           - color: "#FFFFFF"
#           - font-size: "12px"
#           - font-weight: "700"
"""


def generate_lock_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade lock (fechadura)."""
    name = infer_name(entity_id)

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Fechadura / Trava Inteligente
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: "[[[ return entity.state === 'locked' ? '🔒 Trancada' : '🔓 Destrancada' ]]]"
show_label: true
icon: "[[[ return entity.state === 'locked' ? 'mdi:lock' : 'mdi:lock-open' ]]]"
tap_action:
  action: more-info
hold_action:
  action: call-service
  service: lock.toggle
  target:
    entity_id: {entity_id}
  confirmation:
    text: "Deseja alternar o estado da fechadura?"
styles:
  card:
    - background: "[[[ return entity.state === 'locked' ? '{TOKENS['plum']}' : '{TOKENS['card']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "[[[ return entity.state === 'locked' ? '{TOKENS['shadowDark']}' : '{TOKENS['shadowSoft']}' ]]]"
    - min-height: "140px"
    - transition: "all 0.3s"
  icon:
    - color: "[[[ return entity.state === 'locked' ? '#FFFFFF' : '{TOKENS['plum']}' ]]]"
    - width: "20px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'locked' ? 'rgba(255,255,255,0.12)' : '{TOKENS['blush']}' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "[[[ return entity.state === 'locked' ? '#FFFFFF' : '{TOKENS['text']}' ]]]"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "12px"
    - color: "[[[ return entity.state === 'locked' ? 'rgba(255,255,255,0.6)' : '{TOKENS['textMute']}' ]]]"
    - text-align: "left"
"""


def generate_sensor_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade sensor."""
    name = infer_name(entity_id)
    icon = infer_icon(entity_id, "sensor")
    tint = infer_tint(entity_id, TOKENS["mint"])

    if style == "dark":
        bg = TOKENS["plum"]
        text = "#FFFFFF"
        text_mute = "rgba(255,255,255,0.55)"
        icon_bg = "rgba(255,255,255,0.1)"
        icon_color = "#FFFFFF"
        shadow = TOKENS["shadowDark"]
    else:
        bg = TOKENS["card"]
        text = TOKENS["text"]
        text_mute = TOKENS["textMute"]
        icon_bg = "rgba(46,39,66,0.06)"
        icon_color = TOKENS["plum"]
        shadow = TOKENS["shadowSoft"]

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Sensor
type: custom:button-card
entity: {entity_id}
name: "[[[ return entity.state + ' ' + (entity.attributes.unit_of_measurement || '') ]]]"
label: "{name}"
show_label: true
icon: {icon}
tap_action:
  action: more-info
styles:
  card:
    - background: "{bg}"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{shadow}"
    - min-height: "120px"
    - overflow: "hidden"
    - position: "relative"
  icon:
    - color: "{icon_color}"
    - width: "16px"
    - padding: "8px"
    - border-radius: "50%"
    - background: "{icon_bg}"
  name:
    - font-size: "28px"
    - font-weight: "700"
    - letter-spacing: "-0.02em"
    - color: "{text}"
    - margin-top: "14px"
  label:
    - font-size: "10px"
    - font-weight: "700"
    - color: "{text_mute}"
    - text-transform: "uppercase"
    - letter-spacing: "0.06em"
card_mod:
  style: |
    ha-card::after {{
      content: '● LIVE';
      position: absolute;
      top: 14px;
      right: 14px;
      font-size: 10px;
      font-weight: 700;
      color: {TOKENS['orange']};
      letter-spacing: 0.05em;
    }}
    ha-card::before {{
      content: '';
      position: absolute;
      top: -30px;
      right: -30px;
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: {tint};
      opacity: 0.6;
    }}
"""


def generate_binary_sensor_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade binary_sensor."""
    name = infer_name(entity_id)
    icon = infer_icon(entity_id, "binary_sensor")
    tint = infer_tint(entity_id, TOKENS["lavender"])

    is_dark = style == "dark"
    bg_on = TOKENS["plum"] if is_dark else TOKENS["card"]
    bg_off = "rgba(255,255,255,0.06)" if is_dark else TOKENS["cardSoft"]
    text_on = "#FFFFFF" if is_dark else TOKENS["text"]
    text_off = "rgba(255,255,255,0.4)" if is_dark else TOKENS["textMute"]

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Sensor Binário (movimento, presença, porta, janela, etc.)
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: "[[[ return entity.state === 'on' ? 'Detectado' : 'Sem detecção' ]]]"
show_label: true
icon: {icon}
tap_action:
  action: more-info
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '{bg_on}' : '{bg_off}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
    - transition: "all 0.3s"
  icon:
    - color: "[[[ return entity.state === 'on' ? '{TOKENS['orange']}' : '{text_off}' ]]]"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'on' ? '{tint}' : 'rgba(46,39,66,0.06)' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "[[[ return entity.state === 'on' ? '{text_on}' : '{TOKENS['textMute']}' ]]]"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "[[[ return entity.state === 'on' ? 'rgba(255,255,255,0.6)' : '{TOKENS['textFaint']}' ]]]"
    - text-align: "left"
"""


def generate_scene_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade scene."""
    name = infer_name(entity_id)

    color_options = [
        TOKENS["peach"], TOKENS["mint"], TOKENS["lavender"],
        TOKENS["blush"], TOKENS["orange"],
    ]
    # Escolhe cor com base no hash do entity_id (determinístico)
    bg = color_options[hash(entity_id) % len(color_options)]
    is_dark = bg == TOKENS["orange"]
    text = "#FFFFFF" if is_dark else TOKENS["plum"]
    icon_bg = "rgba(255,255,255,0.2)" if is_dark else TOKENS["card"]

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Cena
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: "Toque para ativar"
show_label: true
icon: mdi:palette
tap_action:
  action: call-service
  service: scene.turn_on
  target:
    entity_id: {entity_id}
hold_action:
  action: more-info
styles:
  card:
    - background: "{bg}"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "130px"
    - overflow: "hidden"
    - position: "relative"
    - transition: "transform 0.2s"
  icon:
    - color: "{text}"
    - width: "16px"
    - padding: "8px"
    - border-radius: "50%"
    - background: "{icon_bg}"
    - box-shadow: "{TOKENS['shadowSoft']}"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{text}"
    - text-align: "left"
  label:
    - font-size: "10px"
    - color: "{'rgba(255,255,255,0.7)' if is_dark else 'rgba(46,39,66,0.55)'}"
    - text-align: "left"
"""


def generate_media_player_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade media_player."""
    name = infer_name(entity_id)

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Media Player (Alexa, Sonos, Google Home, TV, etc.)
type: media-control
entity: {entity_id}
card_mod:
  style: |
    ha-card {{
      background: {TOKENS['plum']} !important;
      border-radius: 26px !important;
      box-shadow: {TOKENS['shadowDark']} !important;
      color: #fff !important;
    }}
    ha-card * {{
      color: #fff !important;
    }}
    .controls {{
      background: rgba(255,255,255,0.06) !important;
    }}

---
# Versão compacta (button-card) — mostra estado e artista
type: custom:button-card
entity: {entity_id}
name: >-
  [[[ const t = entity.attributes.media_title;
      const a = entity.attributes.media_artist;
      if (!t) return 'Nenhuma mídia';
      return a ? `${{t}} · ${{a}}` : t; ]]]
label: "[[[ return entity.state === 'playing' ? '▶ Tocando' : entity.state === 'paused' ? '⏸ Pausado' : '⏹ Parado' ]]]"
show_label: true
icon: mdi:speaker
tap_action:
  action: more-info
hold_action:
  action: call-service
  service: media_player.media_play_pause
  target:
    entity_id: {entity_id}
styles:
  card:
    - background: "{TOKENS['plum']}"
    - border-radius: "26px"
    - padding: "16px"
    - box-shadow: "{TOKENS['shadowDark']}"
  icon:
    - color: "#FFFFFF"
    - width: "24px"
    - padding: "14px"
    - border-radius: "14px"
    - background: "linear-gradient(135deg, {TOKENS['orange']}, {TOKENS['peach']})"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "#FFFFFF"
    - text-align: "left"
    - margin-top: "4px"
  label:
    - font-size: "11px"
    - color: "rgba(255,255,255,0.55)"
    - text-align: "left"
    - font-weight: "600"
    - text-transform: "uppercase"
    - letter-spacing: "0.08em"
"""


def generate_input_boolean_card(entity_id: str, style: str = "default") -> str:
    """Gera card para input_boolean."""
    name = infer_name(entity_id)
    icon = "mdi:toggle-switch"

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Interruptor Virtual (input_boolean)
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: "[[[ return entity.state === 'on' ? 'Ativo' : 'Inativo' ]]]"
show_label: true
icon: {icon}
tap_action:
  action: toggle
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '{TOKENS['card']}' : '{TOKENS['cardSoft']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
  icon:
    - color: "[[[ return entity.state === 'on' ? '{TOKENS['orange']}' : '{TOKENS['textMute']}' ]]]"
    - width: "22px"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


def generate_fan_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade fan."""
    name = infer_name(entity_id)

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Ventilador / Fan
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: >-
  [[[ const pct = entity.attributes.percentage;
      if (!pct) return entity.state === 'on' ? 'Ligado' : 'Desligado';
      const speed = pct <= 33 ? 'Baixa' : pct <= 66 ? 'Média' : 'Alta';
      return `${{speed}} · ${{pct}}%`; ]]]
show_label: true
icon: mdi:fan
tap_action:
  action: toggle
hold_action:
  action: more-info
styles:
  card:
    - background: "[[[ return entity.state === 'on' ? '{TOKENS['card']}' : '{TOKENS['cardSoft']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
  icon:
    - color: "[[[ return entity.state === 'on' ? '{TOKENS['mintDeep']}' : '{TOKENS['textMute']}' ]]]"
    - width: "18px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'on' ? '{TOKENS['mint']}' : 'rgba(46,39,66,0.06)' ]]]"
    - animation: "[[[ return entity.state === 'on' ? 'spin 2s linear infinite' : 'none' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


def generate_vacuum_card(entity_id: str, style: str = "default") -> str:
    """Gera card para entidade vacuum."""
    name = infer_name(entity_id)

    return f"""\
# Cartão: {name} ({entity_id})
# Tipo: Robô Aspirador
type: custom:button-card
entity: {entity_id}
name: "{name}"
label: >-
  [[[ const s = entity.state;
      const bat = entity.attributes.battery_level;
      const status = {{
        'cleaning': '🔄 Limpando',
        'docked': '🏠 Na base',
        'idle': '⏸ Pausado',
        'returning': '↩ Voltando',
        'error': '⚠️ Erro',
      }};
      return (status[s] || s) + (bat ? ` · 🔋${{bat}}%` : ''); ]]]
show_label: true
icon: mdi:robot-vacuum
tap_action:
  action: call-service
  service: "[[[ return entity.state === 'cleaning' ? 'vacuum.pause' : 'vacuum.start' ]]]"
  target:
    entity_id: {entity_id}
hold_action:
  action: call-service
  service: vacuum.return_to_base
  target:
    entity_id: {entity_id}
styles:
  card:
    - background: "[[[ return entity.state === 'cleaning' ? '{TOKENS['card']}' : '{TOKENS['cardSoft']}' ]]]"
    - border-radius: "26px"
    - padding: "14px"
    - box-shadow: "{TOKENS['shadowSoft']}"
    - min-height: "120px"
  icon:
    - color: "[[[ return entity.state === 'cleaning' ? '{TOKENS['mintDeep']}' : '{TOKENS['textMute']}' ]]]"
    - width: "22px"
    - padding: "9px"
    - border-radius: "50%"
    - background: "[[[ return entity.state === 'cleaning' ? '{TOKENS['mint']}' : 'rgba(46,39,66,0.06)' ]]]"
  name:
    - font-size: "14px"
    - font-weight: "700"
    - color: "{TOKENS['text']}"
    - text-align: "left"
    - margin-top: "14px"
  label:
    - font-size: "11px"
    - color: "{TOKENS['textMute']}"
    - text-align: "left"
"""


# ── Despachante ─────────────────────────────────────────────────────────────
GENERATORS = {
    "light":         generate_light_card,
    "switch":        generate_switch_card,
    "climate":       generate_climate_card,
    "cover":         generate_cover_card,
    "lock":          generate_lock_card,
    "sensor":        generate_sensor_card,
    "binary_sensor": generate_binary_sensor_card,
    "scene":         generate_scene_card,
    "script":        lambda e, s: generate_scene_card(e, s),   # reusa scene
    "media_player":  generate_media_player_card,
    "input_boolean": generate_input_boolean_card,
    "fan":           generate_fan_card,
    "vacuum":        generate_vacuum_card,
}


def main():
    parser = argparse.ArgumentParser(
        description="🏠 HA Smart Home UI — Gerador de Cartões Lovelace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Exemplos:
              %(prog)s --entity light.sala_pendente_norte
              %(prog)s --entity climate.sala_ac --style dark
              %(prog)s --entity cover.cortinas_sala --output cortinas.yaml
              %(prog)s --entity sensor.temperatura_sala
              %(prog)s --entity binary_sensor.sala_movimento --style dark
              %(prog)s --entity media_player.alexa_sala
              %(prog)s --entity lock.porta_entrada
              %(prog)s --entity switch.cafeteira
              %(prog)s --list-types
        """),
    )
    parser.add_argument(
        "--entity", "-e",
        metavar="ENTITY_ID",
        help="entity_id no formato dominio.nome (ex: light.sala)",
    )
    parser.add_argument(
        "--style", "-s",
        choices=["default", "dark", "minimal"],
        default="default",
        help="Estilo do card: default (cream/branco), dark (plum escuro), minimal (sem sombra)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="ARQUIVO.yaml",
        help="Salvar YAML em arquivo (padrão: stdout)",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="Lista todos os tipos de entidade suportados",
    )

    args = parser.parse_args()

    if args.list_types:
        print("╔══════════════════════════════════════╗")
        print("║  Tipos de entidade suportados        ║")
        print("╠══════════════════════════════════════╣")
        for domain in sorted(GENERATORS.keys()):
            icon = ICON_MAP.get(domain, "mdi:help-circle")
            print(f"║  {domain:<20} {icon:<18}║")
        print("╚══════════════════════════════════════╝")
        return

    if not args.entity:
        parser.print_help()
        sys.exit(1)

    entity_id = args.entity.strip()
    if "." not in entity_id:
        print(f"❌ Formato inválido: '{entity_id}'")
        print("   Use: dominio.nome  (ex: light.sala_pendente)")
        sys.exit(1)

    domain = entity_id.split(".")[0]
    if domain not in GENERATORS:
        print(f"❌ Domínio '{domain}' não suportado.")
        print(f"   Suportados: {', '.join(sorted(GENERATORS.keys()))}")
        sys.exit(1)

    # Gera o YAML
    generator = GENERATORS[domain]
    yaml_output = generator(entity_id, args.style)

    if args.output:
        Path(args.output).write_text(yaml_output, encoding="utf-8")
        print(f"✅ Cartão salvo em: {args.output}")
        print(f"   Entidade: {entity_id}")
        print(f"   Domínio:  {domain}")
        print(f"   Estilo:   {args.style}")
    else:
        print(f"# ── Cartão gerado para: {entity_id} ────────────────")
        print(yaml_output)
        print("# ── Cole o YAML acima em seu painel Lovelace ────────")


if __name__ == "__main__":
    main()

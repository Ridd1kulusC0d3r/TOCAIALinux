#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a identidade visual da TOCAIA OSINT Linux a partir de tokens.json.

    python3 tema/gerar_tema.py --destino ./saida-tema   # inspecionar no seu PC
    python3 tema/gerar_tema.py --destino /              # dentro da ISO (hook)

Escreve, espelhando o sistema de arquivos:
  * tema GTK 3 "TOCAIA"
  * tema de janelas xfwm4 "TOCAIA" (PNGs gerados aqui, só com zlib)
  * esquema de cores do xfce4-terminal
  * wallpaper.svg, logo e ícones das fases
  * padrões do Xfce (xfconf)
  * menu "TOCAIA" com um submenu por fase
  * tela de login (LightDM GTK greeter)

Só biblioteca padrão.
"""

import argparse
import json
import shutil
import struct
import zlib
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
T = json.loads((AQUI / "tokens.json").read_text(encoding="utf-8"))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a=255):
    return (*hex_rgb(h), a)


def escrever(destino, relativo, conteudo):
    caminho = destino / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(conteudo, bytes):
        caminho.write_bytes(conteudo)
    else:
        caminho.write_text(conteudo, encoding="utf-8")
    return caminho


# ---------------------------------------------------------------- PNG

def png(largura, altura, pixels):
    def bloco(tipo, dados):
        corpo = tipo + dados
        return struct.pack(">I", len(dados)) + corpo + struct.pack(">I", zlib.crc32(corpo) & 0xFFFFFFFF)
    cru = b"".join(b"\x00" + bytes(ch for px in linha for ch in px) for linha in pixels)
    ihdr = struct.pack(">IIBBBBB", largura, altura, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", ihdr)
            + bloco(b"IDAT", zlib.compress(cru, 9)) + bloco(b"IEND", b""))


class Tela:
    def __init__(self, w, h, fundo=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.px = [[fundo for _ in range(w)] for _ in range(h)]

    def ponto(self, x, y, cor):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = cor

    def retangulo(self, x0, y0, x1, y1, cor):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[y][x] = cor

    def traco(self, x0, y0, x1, y1, cor, esp=2):
        passos = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) or 1
        for i in range(passos + 1):
            x = x0 + (x1 - x0) * i / passos
            y = y0 + (y1 - y0) * i / passos
            for dx in range(esp):
                for dy in range(esp):
                    self.ponto(int(x) + dx, int(y) + dy, cor)

    def disco(self, cx, cy, r, cor):
        for y in range(self.h):
            for x in range(self.w):
                d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if d <= r:
                    a = cor[3] if r - d >= 1 else int(cor[3] * max(0.0, r - d))
                    self.ponto(x, y, (*cor[:3], a))

    def bytes_png(self):
        return png(self.w, self.h, self.px)


def paleta_terminal():
    c = T
    return [c["fundo"], c["coral"], c["menta"], c["ambar"], c["azul"], c["lilas"], c["menta_media"], c["texto"],
            c["borda_2"], "#F09A8D", c["menta_clara"], "#F2CF85", "#A6CBF0", "#DDC2F6", "#7FE3D0", c["texto_claro"]]


# ---------------------------------------------------------------- GTK 3

def gtk_css():
    c = T
    return f"""/* TOCAIA OSINT Linux — GTK 3 (gerado; edite tokens.json) */
@import url("resource:///org/gtk/libgtk/theme/Adwaita/gtk-contained-dark.css");

@define-color fundo {c['fundo']};
@define-color superficie {c['superficie']};
@define-color superficie_2 {c['superficie_2']};
@define-color borda {c['borda']};
@define-color borda_2 {c['borda_2']};
@define-color texto {c['texto']};
@define-color texto_claro {c['texto_claro']};
@define-color apagado {c['apagado']};
@define-color menta {c['menta']};
@define-color menta_escura {c['menta_escura']};
@define-color ambar {c['ambar']};
@define-color coral {c['coral']};

@define-color theme_bg_color @fundo;
@define-color theme_fg_color @texto;
@define-color theme_base_color @fundo;
@define-color theme_text_color @texto;
@define-color theme_selected_bg_color @menta_escura;
@define-color theme_selected_fg_color @texto_claro;
@define-color accent_color @menta;

window, .background, dialog {{ background-color: @fundo; color: @texto; }}
headerbar, .titlebar {{ background: @superficie; border-bottom: 1px solid @borda; box-shadow: none; color: @texto; }}
headerbar .title {{ font-weight: 600; }}

button {{ background-image: none; background-color: @superficie_2; border: 1px solid @borda; border-radius: 8px;
          box-shadow: none; color: @texto; text-shadow: none; }}
button:hover {{ border-color: @menta_escura; background-color: shade(@superficie_2, 1.15); }}
button:active, button:checked {{ background-color: alpha(@menta, 0.18); border-color: @menta; color: @menta; }}
button:disabled {{ color: @apagado; background-color: @superficie; }}
button.suggested-action {{ background-color: @menta; border-color: @menta; color: @fundo; }}
button.destructive-action {{ background-color: @coral; border-color: @coral; color: @fundo; }}
button.flat {{ background: transparent; border-color: transparent; }}
button.flat:hover {{ background-color: alpha(@menta, 0.10); }}

entry, spinbutton {{ background-color: @fundo; border: 1px solid @borda_2; border-radius: 8px; color: @texto; box-shadow: none; }}
entry:focus, spinbutton:focus {{ border-color: @menta; box-shadow: 0 0 0 1px alpha(@menta, 0.35); }}

selection, *:selected, row:selected, treeview.view:selected, iconview:selected {{ background-color: alpha(@menta, 0.24); color: @texto_claro; }}
.view, textview text, iconview, treeview.view, list {{ background-color: @fundo; color: @texto; }}
treeview.view header button {{ background-color: @superficie; border-radius: 0; border-width: 0 0 1px 0; }}
row:hover {{ background-color: alpha(@menta, 0.06); }}

menu, .menu, .context-menu, popover, popover.background {{ background-color: @superficie; border: 1px solid @borda; color: @texto; }}
menuitem {{ padding: 6px 10px; }}
menuitem:hover, menu menuitem:hover {{ background-color: alpha(@menta, 0.14); color: @menta; }}
menubar {{ background-color: @fundo; border-bottom: 1px solid @borda; }}

scrollbar {{ background: transparent; border: none; }}
scrollbar slider {{ background-color: @borda_2; border-radius: 8px; min-width: 6px; min-height: 6px; border: 2px solid transparent; }}
scrollbar slider:hover {{ background-color: @menta_escura; }}

notebook > header {{ background-color: @superficie; border-color: @borda; }}
notebook > header tab {{ color: @apagado; }}
notebook > header tab:checked {{ color: @menta; box-shadow: inset 0 -2px @menta; }}

check:checked, radio:checked {{ background-image: none; background-color: @menta; border-color: @menta; color: @fundo; }}
switch:checked {{ background-color: @menta; border-color: @menta; }}
progressbar progress, scale highlight, levelbar block.filled {{ background-color: @menta; border-color: @menta; }}
scale slider {{ background-color: @texto; border-color: @menta_escura; }}
link, *:link, button.link {{ color: @menta; }}
tooltip, tooltip.background {{ background-color: @superficie; border: 1px solid @borda; color: @texto; border-radius: 8px; }}
separator {{ background-color: @borda; }}
infobar.warning > revealer > box {{ background-color: alpha(@ambar, 0.18); color: @texto; }}
infobar.error > revealer > box {{ background-color: alpha(@coral, 0.20); color: @texto; }}

.xfce4-panel {{ background-color: @fundo; color: @texto; border-bottom: 1px solid @borda; }}
.xfce4-panel button {{ border: none; background: transparent; border-radius: 6px; padding: 2px 8px; }}
.xfce4-panel button:hover {{ background-color: alpha(@menta, 0.10); }}
.xfce4-panel button:checked {{ background-color: alpha(@menta, 0.16); color: @menta; box-shadow: inset 0 -2px @menta; }}
#whiskermenu-window {{ background-color: @superficie; border: 1px solid @borda; }}
.thunar .sidebar {{ background-color: @superficie; }}
.thunar .path-bar button {{ border-radius: 6px; }}
"""


def gtk_settings_ini():
    return (f"[Settings]\ngtk-theme-name=TOCAIA\ngtk-icon-theme-name=Papirus-Dark\n"
            f"gtk-font-name={T['fontes']['interface']} 10\ngtk-application-prefer-dark-theme=1\n")


def terminal_scheme():
    return f"""[Scheme]
Name=TOCAIA
ColorForeground={T['texto']}
ColorBackground={T['fundo']}
ColorCursor={T['menta']}
ColorCursorUseDefault=FALSE
ColorBold={T['texto_claro']}
ColorBoldUseDefault=FALSE
ColorSelection={T['menta_funda']}
ColorSelectionUseDefault=FALSE
ColorPalette={';'.join(paleta_terminal())}
"""


# ---------------------------------------------------------------- xfwm4

ALT = 30   # altura da barra de título
BOR = 2    # espessura da borda


def _glifo(t, tipo, cor):
    m = ALT // 2
    if tipo == "close":
        t.traco(m - 4, m - 4, m + 4, m + 4, cor)
        t.traco(m - 4, m + 4, m + 4, m - 4, cor)
    elif tipo == "hide":
        t.traco(m - 5, m + 3, m + 5, m + 3, cor)
    elif tipo == "maximize":
        for a in ((m - 5, m - 5, m + 5, m - 5), (m + 5, m - 5, m + 5, m + 5),
                  (m + 5, m + 5, m - 5, m + 5), (m - 5, m + 5, m - 5, m - 5)):
            t.traco(*a, cor)
    elif tipo == "maximize-toggled":
        for a in ((m - 5, m - 2, m + 2, m - 2), (m + 2, m - 2, m + 2, m + 5),
                  (m + 2, m + 5, m - 5, m + 5), (m - 5, m + 5, m - 5, m - 2),
                  (m - 2, m - 5, m + 5, m - 5), (m + 5, m - 5, m + 5, m + 2)):
            t.traco(*a, cor)
    elif tipo == "menu":  # o losango do OSINT no Jutsu
        for a in ((m, m - 6, m + 6, m), (m + 6, m, m, m + 6),
                  (m, m + 6, m - 6, m), (m - 6, m, m, m - 6)):
            t.traco(*a, cor)
    else:
        t.disco(m, m, 2.5, cor)


def xfwm4_arquivos():
    arqs = {}
    for estado, cor_base in (("active", T["menta_escura"]), ("inactive", T["borda"])):
        fundo = rgba(T["superficie"] if estado == "active" else T["fundo_2"])
        for nome in ("title-1", "title-2", "title-3", "title-4", "title-5", "top-left", "top-right"):
            larg = 8 if nome.startswith("title") else 6
            t = Tela(larg, ALT, fundo)
            t.retangulo(0, ALT - 1, larg, ALT, rgba(cor_base))
            if nome == "top-left":
                t.retangulo(0, 0, BOR, ALT, rgba(T["borda"]))
            if nome == "top-right":
                t.retangulo(larg - BOR, 0, larg, ALT, rgba(T["borda"]))
            arqs[f"{nome}-{estado}.png"] = t.bytes_png()
        for nome, (w, h) in {"left": (BOR, 8), "right": (BOR, 8), "bottom": (8, BOR),
                             "bottom-left": (BOR, BOR), "bottom-right": (BOR, BOR)}.items():
            arqs[f"{nome}-{estado}.png"] = Tela(w, h, rgba(T["borda"])).bytes_png()

    tipos = ["close", "hide", "maximize", "maximize-toggled", "menu",
             "shade", "shade-toggled", "stick", "stick-toggled"]
    for tipo in tipos:
        base = "shade" if tipo.startswith("shade") else ("stick" if tipo.startswith("stick") else tipo)
        for estado in ("active", "inactive", "prelight", "pressed"):
            fundo = rgba(T["superficie"] if estado != "inactive" else T["fundo_2"])
            t = Tela(ALT, ALT, fundo)
            t.retangulo(0, ALT - 1, ALT, ALT, rgba(T["menta_escura"] if estado != "inactive" else T["borda"]))
            realce = T["coral"] if base == "close" else T["menta"]
            if estado == "prelight":
                t.disco(ALT / 2, ALT / 2, 11, rgba(realce, 40)); cor = rgba(realce)
            elif estado == "pressed":
                t.disco(ALT / 2, ALT / 2, 11, rgba(realce, 90)); cor = rgba(T["texto_claro"])
            elif estado == "inactive":
                cor = rgba(T["inativo"])
            else:
                cor = rgba(T["menta"] if base == "menu" else T["apagado"])
            _glifo(t, base if base in ("shade", "stick") else tipo, cor)
            arqs[f"{tipo}-{estado}.png"] = t.bytes_png()

    arqs["themerc"] = f"""# TOCAIA — xfwm4 (gerado)
button_offset=6
button_spacing=4
full_width_title=true
title_alignment=center
title_vertical_offset_active=0
title_vertical_offset_inactive=0
title_shadow_active=false
title_shadow_inactive=false
active_text_color={T['texto']}
inactive_text_color={T['inativo']}
"""
    return arqs


# ---------------------------------------------------------------- SVG

def logo_svg(tam=256):
    m = tam / 2
    r = tam * 0.44
    d = tam * 0.22
    lg = tam * 0.035
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tam} {tam}" width="{tam}" height="{tam}">
  <circle cx="{m}" cy="{m}" r="{r}" fill="{T['fundo']}" stroke="{T['menta']}" stroke-width="{lg}"/>
  <path d="M{m} {m - d} L{m + d} {m} L{m} {m + d} L{m - d} {m} Z" fill="none" stroke="{T['menta']}" stroke-width="{lg}" stroke-linejoin="round"/>
  <path d="M{m} {m - d * 0.55} L{m + d * 0.55} {m} L{m} {m + d * 0.55} L{m - d * 0.55} {m} Z" fill="{T['menta']}" fill-opacity="0.18"/>
</svg>
"""


def icone_fase(letra):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect x="3" y="3" width="58" height="58" rx="14" fill="{T['superficie']}" stroke="{T['menta_escura']}" stroke-width="2"/>
  <text x="32" y="44" text-anchor="middle" font-family="{T['fontes']['mono']}, monospace" font-weight="700" font-size="32" fill="{T['menta']}">{letra}</text>
</svg>
"""


def wallpaper_svg(w=1920, h=1080):
    c = T
    grade = []
    for x in range(0, w + 1, 48):
        grade.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>')
    for y in range(0, h + 1, 48):
        grade.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}"/>')
    cx, cy = w * 0.70, h * 0.50
    ybase = h * 0.36
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{c['menta_clara']}"/>
      <stop offset="0.55" stop-color="{c['menta']}"/>
      <stop offset="1" stop-color="{c['menta_escura']}"/>
    </linearGradient>
    <radialGradient id="halo" cx="{cx / w}" cy="{cy / h}" r="0.45">
      <stop offset="0" stop-color="{c['menta']}" stop-opacity="0.07"/>
      <stop offset="1" stop-color="{c['menta']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="{c['fundo']}"/>
  <g stroke="#FFFFFF" stroke-opacity="0.025" stroke-width="1">{''.join(grade)}</g>
  <rect width="{w}" height="{h}" fill="url(#halo)"/>
  <g fill="none" stroke="{c['menta']}">
    <circle cx="{cx}" cy="{cy}" r="330" stroke-opacity="0.10"/>
    <circle cx="{cx}" cy="{cy}" r="220" stroke-opacity="0.18"/>
    <circle cx="{cx}" cy="{cy}" r="120" stroke-opacity="0.32"/>
    <circle cx="{cx}" cy="{cy}" r="44" stroke-opacity="0.55"/>
    <line x1="{cx - 380}" y1="{cy}" x2="{cx + 380}" y2="{cy}" stroke-opacity="0.12"/>
    <line x1="{cx}" y1="{cy - 380}" x2="{cx}" y2="{cy + 380}" stroke-opacity="0.12"/>
  </g>
  <g stroke="{c['menta']}" stroke-opacity="0.75" stroke-width="2">
    <line x1="{cx - 300}" y1="{cy - 250}" x2="{cx - 30}" y2="{cy - 22}"/>
    <line x1="{cx - 300}" y1="{cy + 250}" x2="{cx - 30}" y2="{cy + 22}"/>
    <line x1="{cx + 400}" y1="{cy}" x2="{cx + 44}" y2="{cy}"/>
  </g>
  <g fill="{c['menta']}">
    <circle cx="{cx - 300}" cy="{cy - 250}" r="5"/><circle cx="{cx - 300}" cy="{cy + 250}" r="5"/><circle cx="{cx + 400}" cy="{cy}" r="5"/>
  </g>
  <g font-family="{c['fontes']['mono']}, monospace" font-size="15" letter-spacing="5" fill="{c['apagado']}">
    <text x="{cx - 300}" y="{cy - 272}" text-anchor="middle">PSICOLOGIA</text>
    <text x="{cx - 300}" y="{cy + 286}" text-anchor="middle">PADRÕES</text>
    <text x="{cx + 400}" y="{cy - 18}" text-anchor="middle">AUSÊNCIA</text>
  </g>
  <text x="140" y="{ybase}" font-family="{c['fontes']['mono']}, monospace" letter-spacing="7" font-size="16" fill="{c['apagado']}">OSINT · LINUX · 1.0 TROPEIRO</text>
  <text x="132" y="{ybase + 150}" font-family="{c['fontes']['titulo']}, sans-serif" font-weight="800" font-size="168" letter-spacing="-4" fill="url(#g)">TOCAIA</text>
  <line x1="140" y1="{ybase + 186}" x2="760" y2="{ybase + 186}" stroke="{c['menta']}" stroke-opacity="0.6"/>
  <text x="140" y="{ybase + 232}" font-family="{c['fontes']['mono']}, monospace" font-size="18" letter-spacing="4" fill="{c['texto']}">LEIA O PADRÃO · OUÇA O SILÊNCIO · <tspan fill="{c['menta']}">POSICIONE-SE E ESPERE</tspan></text>
  <text x="140" y="{h - 70}" font-family="{c['fontes']['mono']}, monospace" font-size="13" letter-spacing="4" fill="{c['inativo']}">DEIVOSINT · OSINT NO JUTSU</text>
</svg>
"""


# ---------------------------------------------------------------- xfconf

def _canal(nome, corpo):
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<channel name="{nome}" version="1.0">\n{corpo}</channel>\n'


def xfconf_xsettings():
    f = T["fontes"]
    return _canal("xsettings", f"""  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="TOCAIA"/>
    <property name="IconThemeName" type="string" value="Papirus-Dark"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="FontName" type="string" value="{f['interface']} 10"/>
    <property name="MonospaceFontName" type="string" value="{f['mono']} 10"/>
  </property>
  <property name="Xft" type="empty">
    <property name="Antialias" type="int" value="1"/>
    <property name="HintStyle" type="string" value="hintslight"/>
    <property name="RGBA" type="string" value="rgb"/>
  </property>
""")


def xfconf_xfwm4():
    return _canal("xfwm4", f"""  <property name="general" type="empty">
    <property name="theme" type="string" value="TOCAIA"/>
    <property name="title_font" type="string" value="{T['fontes']['interface']} Semi-Bold 10"/>
    <property name="title_alignment" type="string" value="center"/>
    <property name="button_layout" type="string" value="O|HMC"/>
    <property name="use_compositing" type="bool" value="true"/>
    <property name="show_frame_shadow" type="bool" value="false"/>
    <property name="workspace_count" type="int" value="2"/>
  </property>
""")


def xfconf_terminal():
    return _canal("xfce4-terminal", f"""  <property name="font-name" type="string" value="{T['fontes']['mono']} 11"/>
  <property name="font-use-system" type="bool" value="false"/>
  <property name="color-foreground" type="string" value="{T['texto']}"/>
  <property name="color-background" type="string" value="{T['fundo']}"/>
  <property name="color-cursor" type="string" value="{T['menta']}"/>
  <property name="color-cursor-use-default" type="bool" value="false"/>
  <property name="color-selection" type="string" value="{T['menta_funda']}"/>
  <property name="color-selection-use-default" type="bool" value="false"/>
  <property name="color-palette" type="string" value="{';'.join(paleta_terminal())}"/>
  <property name="misc-menubar-default" type="bool" value="false"/>
  <property name="misc-default-geometry" type="string" value="110x30"/>
  <property name="scrolling-bar" type="string" value="TERMINAL_SCROLLBAR_NONE"/>
""")


_MONITORES = ["monitorVirtual-1", "monitorVirtual1", "monitorVGA-1", "monitorHDMI-1",
              "monitoreDP-1", "monitorDP-1", "monitorLVDS-1", "monitor0", "monitorscreen"]


def xfconf_desktop():
    blocos = []
    for m in _MONITORES:
        ws = "".join(f"""          <property name="workspace{i}" type="empty">
            <property name="last-image" type="string" value="/usr/share/tocaia/wallpaper.png"/>
            <property name="image-style" type="int" value="5"/>
          </property>
""" for i in (0, 1))
        blocos.append(f'        <property name="{m}" type="empty">\n{ws}        </property>\n')
    return _canal("xfce4-desktop", f"""  <property name="desktop-icons" type="empty">
    <property name="style" type="int" value="0"/>
  </property>
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
{''.join(blocos)}    </property>
  </property>
""")


def xfconf_painel():
    r, g, b = (v / 255 for v in hex_rgb(T["fundo"]))
    return _canal("xfce4-panel", f"""  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="dark-mode" type="bool" value="true"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="34"/>
      <property name="icon-size" type="uint" value="18"/>
      <property name="background-style" type="uint" value="1"/>
      <property name="background-rgba" type="array">
        <value type="double" value="{r:.3f}"/>
        <value type="double" value="{g:.3f}"/>
        <value type="double" value="{b:.3f}"/>
        <value type="double" value="0.96"/>
      </property>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/><value type="int" value="2"/><value type="int" value="3"/>
        <value type="int" value="4"/><value type="int" value="5"/><value type="int" value="6"/>
        <value type="int" value="7"/><value type="int" value="8"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="applicationsmenu">
      <property name="button-title" type="string" value="TOCAIA"/>
      <property name="show-button-title" type="bool" value="true"/>
      <property name="button-icon" type="string" value="tocaia"/>
    </property>
    <property name="plugin-2" type="string" value="separator"/>
    <property name="plugin-3" type="string" value="pager"/>
    <property name="plugin-4" type="string" value="tasklist">
      <property name="flat-buttons" type="bool" value="true"/>
    </property>
    <property name="plugin-5" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-6" type="string" value="systray"/>
    <property name="plugin-7" type="string" value="clock">
      <property name="digital-time-format" type="string" value="%a %d · %H:%M"/>
    </property>
    <property name="plugin-8" type="string" value="actions"/>
  </property>
""")


# ---------------------------------------------------------------- menu por fases

def _carregar_fases():
    for c in (AQUI.parent / "catalogo.json", AQUI.parent / "catalogo" / "catalogo.json"):
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))["fases"]
    raise SystemExit("gerar_tema: não achei o catalogo.json")


def _sem_cedilha(s):
    return s.replace("ç", "c").replace("Ç", "C")


def menu_xml(fases):
    sub, layout = [], []
    for chave, f in fases.items():
        cat = "X-TOCAIA-" + _sem_cedilha(f["nome"])
        layout.append(f"      <Menuname>tocaia-{chave}</Menuname>")
        sub.append(f"""    <Menu>
      <Name>tocaia-{chave}</Name>
      <Directory>tocaia-{chave}.directory</Directory>
      <Include><Category>{cat}</Category></Include>
    </Menu>""")
    return f"""<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
  "http://www.freedesktop.org/standards/menu-spec/menu-1.0.dtd">
<!-- TOCAIA: o menu segue a doutrina, não o tipo de ferramenta (gerado) -->
<Menu>
  <Name>Applications</Name>
  <Menu>
    <Name>TOCAIA</Name>
    <Directory>tocaia.directory</Directory>
    <Include>
      <Filename>tocaia-manual.desktop</Filename>
      <Filename>tocaia-terminal.desktop</Filename>
    </Include>
    <Layout>
      <Filename>tocaia-manual.desktop</Filename>
      <Filename>tocaia-terminal.desktop</Filename>
      <Separator/>
{chr(10).join(layout)}
    </Layout>
{chr(10).join(sub)}
  </Menu>
</Menu>
"""


def arquivos_menu(fases):
    arqs = {
        "etc/xdg/menus/applications-merged/tocaia.menu": menu_xml(fases),
        "usr/share/desktop-directories/tocaia.directory":
            "[Desktop Entry]\nType=Directory\nName=TOCAIA\nComment=OSINT pelo metodo\nIcon=tocaia\n",
        "usr/share/applications/tocaia-manual.desktop":
            "[Desktop Entry]\nType=Application\nName=Manual da TOCAIA\nComment=Comece por aqui\n"
            "Exec=xdg-open /usr/share/tocaia/manual/index.html\nIcon=tocaia\nCategories=X-TOCAIA-Tracar;\n",
        "usr/share/applications/tocaia-terminal.desktop":
            "[Desktop Entry]\nType=Application\nName=Terminal TOCAIA\nComment=trem na linha de comando\n"
            "Exec=xfce4-terminal\nIcon=utilities-terminal\nCategories=X-TOCAIA-Observar;\n",
    }
    for chave, f in fases.items():
        ordem = list(fases).index(chave) + 1
        arqs[f"usr/share/desktop-directories/tocaia-{chave}.directory"] = (
            f"[Desktop Entry]\nType=Directory\nName={ordem} · {f['letra']} — {f['nome']}\n"
            f"Comment={f['lema']}\nIcon=tocaia-{chave}\n")
    return arqs


# ---------------------------------------------------------------- LightDM (login)

def lightdm_conf():
    # usa a tela de login fotográfica se existir; senão, o wallpaper
    fundo = "/usr/share/tocaia/login.png"
    return f"""[greeter]
background = {fundo}
theme-name = TOCAIA
icon-theme-name = Papirus-Dark
font-name = {T['fontes']['interface']} 10
xft-antialias = true
xft-hintstyle = hintslight
indicators = ~host;~spacer;~clock;~spacer;~session;~power
clock-format = %A, %d de %B  %H:%M
position = 50%,center 55%,center
"""


# ---------------------------------------------------------------- GRUB

def grub_tema():
    c = T
    return f"""# TOCAIA — tema do GRUB (gerado)
title-text: ""
desktop-color: "{c['fundo']}"
desktop-image: "background.png"
desktop-image-scale-method: "crop"
terminal-font: "Unifont Regular 16"
terminal-left: "0"
terminal-top: "0"
+ boot_menu {{
    left = 18%
    top = 32%
    width = 64%
    height = 50%
    item_font = "Unifont Regular 16"
    item_color = "{c['apagado']}"
    selected_item_color = "{c['menta']}"
    item_height = 34
    item_spacing = 8
    icon_width = 0
    icon_height = 0
}}
+ label {{
    top = 20%
    left = 18%
    width = 64%
    align = "left"
    color = "{c['menta']}"
    font = "Unifont Regular 16"
    text = "TOCAIA OSINT Linux 1.0 Tropeiro"
}}
+ label {{
    top = 88%
    left = 18%
    width = 64%
    align = "left"
    color = "{c['inativo']}"
    font = "Unifont Regular 16"
    text = "leia o padrao - ouca o silencio - posicione-se e espere"
}}
"""


# ---------------------------------------------------------------- orquestração

def gerar(destino):
    """Escreve tudo sob 'destino' (que vira a raiz /)."""
    destino = Path(destino)
    tema = "usr/share/themes/TOCAIA"
    tc = "usr/share/tocaia"
    fases = _carregar_fases()

    # GTK
    escrever(destino, f"{tema}/gtk-3.0/gtk.css", gtk_css())
    escrever(destino, f"{tema}/gtk-3.0/gtk-dark.css", gtk_css())
    escrever(destino, f"{tema}/index.theme",
             "[Desktop Entry]\nType=X-GNOME-Metatheme\nName=TOCAIA\nComment=OSINT no Jutsu\n"
             "Encoding=UTF-8\n[X-GNOME-Metatheme]\nGtkTheme=TOCAIA\nMetacityTheme=TOCAIA\n"
             "IconTheme=Papirus-Dark\nButtonLayout=O:HMC\n")
    escrever(destino, "etc/skel/.config/gtk-3.0/settings.ini", gtk_settings_ini())

    # xfwm4
    for nome, conteudo in xfwm4_arquivos().items():
        escrever(destino, f"{tema}/xfwm4/{nome}", conteudo)

    # terminal (esquema instalável)
    escrever(destino, "usr/share/xfce4/terminal/colorschemes/tocaia.theme", terminal_scheme())

    # SVGs + PNGs de marca
    escrever(destino, f"{tc}/logo.svg", logo_svg())
    escrever(destino, f"{tc}/wallpaper.svg", wallpaper_svg())
    for chave, f in fases.items():
        escrever(destino, f"{tc}/icones/tocaia-{chave}.svg", icone_fase(f["letra"]))
    # logo rasterizado (256x256) para o menu, caso não haja conversor de SVG na ISO
    escrever(destino, f"{tc}/logo.png", _logo_png())

    # xfconf (padrões aplicados a cada novo usuário via /etc/skel)
    base_xfconf = "etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml"
    escrever(destino, f"{base_xfconf}/xsettings.xml", xfconf_xsettings())
    escrever(destino, f"{base_xfconf}/xfwm4.xml", xfconf_xfwm4())
    escrever(destino, f"{base_xfconf}/xfce4-terminal.xml", xfconf_terminal())
    escrever(destino, f"{base_xfconf}/xfce4-desktop.xml", xfconf_desktop())
    escrever(destino, f"{base_xfconf}/xfce4-panel.xml", xfconf_painel())

    # menu por fases
    for rel, conteudo in arquivos_menu(fases).items():
        escrever(destino, rel, conteudo)

    # login e grub
    escrever(destino, "etc/lightdm/lightdm-gtk-greeter.conf", lightdm_conf())
    escrever(destino, "boot/grub/themes/tocaia/theme.txt", grub_tema())

    # marca fotográfica (onça/face), se já gerada em assets/gerado
    instalar_marca(destino)

    print(f"✓ tema TOCAIA escrito em {destino}")
    return destino


def instalar_marca(destino):
    """Integra as artes da marca (onça na espreita e face de olhos ciano).

    Lê de assets/gerado (produzido por assets/gerar_marca.py). Se não existir,
    o tema continua com o wallpaper vetorial e o logo-losango — nada quebra.
    """
    destino = Path(destino)
    marca = RAIZ / "assets" / "gerado"
    tc = destino / "usr/share/tocaia"
    if not marca.exists():
        return False

    # wallpaper principal = a espreita (SVG com wordmark; o hook rasteriza p/ .png)
    if (marca / "wallpaper-espreita.svg").exists():
        escrever(destino, "usr/share/tocaia/wallpaper.svg",
                 (marca / "wallpaper-espreita.svg").read_text(encoding="utf-8"))
    for nome in ("wallpaper-face.svg", "login.svg"):
        if (marca / nome).exists():
            escrever(destino, f"usr/share/tocaia/{nome}", (marca / nome).read_text(encoding="utf-8"))
    for nome in ("login.png", "grub.png", "wallpaper-espreita-base.png"):
        if (marca / nome).exists():
            (tc).mkdir(parents=True, exist_ok=True)
            shutil.copy(marca / nome, tc / nome)

    # ícone do app 'tocaia' a partir da face (menu, janelas, barra)
    for png in (marca / "icones").glob("tocaia-face-*.png"):
        tam = png.stem.rsplit("-", 1)[1]
        dest = destino / f"usr/share/icons/hicolor/{tam}x{tam}/apps"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy(png, dest / "tocaia.png")

    # fundo do menu de boot (GRUB) — seguro: só uma imagem no tema
    if (marca / "grub.png").exists():
        escrever(destino, "boot/grub/themes/tocaia/background.png", (marca / "grub.png").read_bytes())

    # a face fica disponível para o boot splash (Plymouth) de uma versão futura,
    # sem ativá-lo agora (evita qualquer risco no boot).
    if (marca / "plymouth" / "tocaia-face.png").exists():
        shutil.copy(marca / "plymouth" / "tocaia-face.png", tc / "face.png")
    return True


def _logo_png(tam=256):
    """Logo rasterizado só com nossos primitivos (sem depender de conversor de SVG)."""
    m = tam / 2
    t = Tela(tam, tam, rgba(T["fundo"], 0))
    t.disco(m, m, tam * 0.46, rgba(T["fundo"]))
    t.disco(m, m, tam * 0.46, rgba(T["menta"]))
    t.disco(m, m, tam * 0.46 - tam * 0.035, rgba(T["fundo"]))
    d = tam * 0.22
    for a in ((m, m - d, m + d, m), (m + d, m, m, m + d), (m, m + d, m - d, m), (m - d, m, m, m - d)):
        t.traco(*a, rgba(T["menta"]), esp=max(2, int(tam * 0.02)))
    return t.bytes_png()


def main(argv=None):
    p = argparse.ArgumentParser(description="Gera o tema da TOCAIA OSINT Linux.")
    p.add_argument("--destino", default="./saida-tema", help="raiz onde escrever (padrão: ./saida-tema)")
    a = p.parse_args(argv)
    gerar(a.destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


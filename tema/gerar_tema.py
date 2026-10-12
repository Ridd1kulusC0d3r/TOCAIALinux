#!/usr/bin/env python3
"""Gera o visual da TOCAIA a partir de tema/paleta.json. Só stdlib.

Saída vai para dentro da árvore do live-build (iso/config/includes.chroot):
GTK, Xfce (xsettings, xfwm4, terminal), tela de login e wallpaper SVG.
Mudou uma cor? Edite a paleta e rode de novo: tudo acompanha.

    python3 tema/gerar_tema.py [pasta_destino]
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
P = json.loads((RAIZ / "tema" / "paleta.json").read_text(encoding="utf-8"))


def gtk_css():
    return f"""/* TOCAIA — sobre o Adwaita-dark. Gerado por tema/gerar_tema.py */
@define-color theme_bg_color {P['superficie']};
@define-color theme_base_color {P['fundo']};
@define-color theme_fg_color {P['texto']};
@define-color theme_text_color {P['texto']};
@define-color theme_selected_bg_color {P['menta_escuro']};
@define-color theme_selected_fg_color {P['fundo']};
@define-color borders {P['borda']};
@define-color warning_color {P['ambar']};
@define-color error_color {P['coral']};
@define-color accent_bg_color {P['menta_escuro']};
@define-color accent_color {P['menta']};
"""


def xsettings():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Adwaita-dark"/>
    <property name="IconThemeName" type="string" value="Papirus-Dark"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="FontName" type="string" value="{P['fontes']['titulo']} 10"/>
    <property name="MonospaceFontName" type="string" value="{P['fontes']['mono']} 10"/>
  </property>
</channel>
"""


def xfwm4():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Greybird-dark"/>
    <property name="title_font" type="string" value="{P['fontes']['titulo']} Bold 9"/>
    <property name="use_compositing" type="bool" value="false"/>
  </property>
</channel>
"""


def terminal():
    paleta16 = ";".join([P["fundo"], P["coral"], P["menta_escuro"], P["ambar"], "#5B8DEF",
                         "#B48EAD", P["menta"], P["texto"], P["borda"], P["coral"],
                         P["menta"], P["ambar"], "#82AAFF", "#C9A0DC", P["menta_claro"], "#FFFFFF"])
    return f"""[Configuration]
FontName={P['fontes']['mono']} 11
ColorForeground={P['texto']}
ColorBackground={P['fundo']}
ColorCursor={P['menta']}
ColorSelection={P['menta_escuro']}
ColorPalette={paleta16}
MiscMenubarDefault=FALSE
ScrollingBar=TERMINAL_SCROLLBAR_NONE
"""


def greeter():
    return f"""[greeter]
background=/usr/share/backgrounds/tocaia/tocaia.svg
theme-name=Adwaita-dark
icon-theme-name=Papirus-Dark
font-name={P['fontes']['titulo']} 11
indicators=~host;~spacer;~clock;~spacer;~session;~power
clock-format=%d/%m %H:%M
"""


def wallpaper():
    aneis = "".join(
        f'<circle cx="960" cy="540" r="{r}" fill="none" stroke="{P["menta"]}" '
        f'stroke-opacity="{op}" stroke-width="1.5"/>'
        for r, op in ((120, .55), (220, .35), (330, .22), (450, .12)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs>
    <pattern id="grade" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M48 0H0V48" fill="none" stroke="{P['borda']}" stroke-width="1"/>
    </pattern>
    <linearGradient id="menta" x1="0" x2="1">
      <stop offset="0" stop-color="{P['menta_claro']}"/>
      <stop offset="1" stop-color="{P['menta_escuro']}"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="{P['fundo']}"/>
  <rect width="1920" height="1080" fill="url(#grade)" opacity=".6"/>
  {aneis}
  <path d="M960 380V470M960 610V700M800 540H890M1030 540H1120" stroke="{P['menta']}" stroke-width="2"/>
  <circle cx="960" cy="540" r="4" fill="{P['coral']}"/>
  <text x="960" y="900" text-anchor="middle" font-family="{P['fontes']['titulo']}, sans-serif"
        font-size="64" font-weight="700" letter-spacing="18" fill="url(#menta)">TOCAIA</text>
  <text x="960" y="945" text-anchor="middle" font-family="{P['fontes']['mono']}, monospace"
        font-size="18" letter-spacing="6" fill="{P['texto_apagado']}">OSINT LINUX · TROPEIRO</text>
</svg>
"""


ARQUIVOS = {
    "etc/skel/.config/gtk-3.0/gtk.css": gtk_css,
    "etc/skel/.config/gtk-3.0/settings.ini":
        lambda: "[Settings]\ngtk-theme-name=Adwaita-dark\ngtk-icon-theme-name=Papirus-Dark\n"
                f"gtk-font-name={P['fontes']['titulo']} 10\n",
    "etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml": xsettings,
    "etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml": xfwm4,
    "etc/skel/.config/xfce4/terminal/terminalrc": terminal,
    "etc/lightdm/lightdm-gtk-greeter.conf": greeter,
    "usr/share/backgrounds/tocaia/tocaia.svg": wallpaper,
}


def main(destino=None):
    raiz = Path(destino) if destino else RAIZ / "iso" / "config" / "includes.chroot"
    for rel, gerar in ARQUIVOS.items():
        alvo = raiz / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(gerar(), encoding="utf-8")
    print(f"tema gerado: {len(ARQUIVOS)} arquivos em {raiz}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))

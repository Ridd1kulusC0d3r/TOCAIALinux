#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integra as artes da marca (a onça na espreita e a face de olhos ciano) nas
telas do sistema, casando-as com a paleta de tema/paleta.json.

    python3 assets/gerar_marca.py [pasta_destino]

Roda DEPOIS de tema/gerar_tema.py (o construir-iso.sh já faz isso) e escreve
dentro de iso/config/includes.chroot:

  usr/share/backgrounds/tocaia/tocaia.svg       ← wallpaper = a onça + wordmark
                                                  (o desktop e o login já apontam aqui)
  usr/share/backgrounds/tocaia/tocaia-face.svg  ← variante: a face de olhos ciano
  usr/share/backgrounds/tocaia/tocaia-mira.svg  ← preserva o wallpaper vetorial original
  usr/share/backgrounds/tocaia/login.png        ← fundo de login com a face (opcional)
  usr/share/icons/hicolor/<tam>/apps/tocaia.png ← ícone do app = a face
  usr/share/pixmaps/tocaia.png

Precisa de Pillow (só para recortar/escalar as fotos e gerar os ícones). Se o
Pillow não estiver disponível, o construir-iso.sh segue com o wallpaper vetorial.
Fonte única das cores: tema/paleta.json (as mesmas do resto do tema).
"""
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

RAIZ = Path(__file__).resolve().parent.parent
MARCA = RAIZ / "assets" / "marca"
P = json.loads((RAIZ / "tema" / "paleta.json").read_text(encoding="utf-8"))

# apelidos tolerantes (a paleta pode não ter todos os tons)
MENTA = P["menta"]
MENTA_CLARO = P.get("menta_claro", P["menta"])
MENTA_ESCURO = P.get("menta_escuro", P["menta"])
TEXTO = P["texto"]
APAGADO = P.get("texto_apagado", "#8A9693")
FUNDO = P["fundo"]
TITULO = P["fontes"]["titulo"]
MONO = P["fontes"]["mono"]


def b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def cobrir(img, w, h):
    r = max(w / img.width, h / img.height)
    novo = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    x = (novo.width - w) // 2
    y = (novo.height - h) // 2
    return novo.crop((x, y, x + w, y + h))


def wallpaper_svg(foto_b64, titulo=True):
    yb = 648
    bloco = f"""
  <text x="140" y="{yb-36}" font-family="{MONO},monospace" font-size="15" letter-spacing="7" fill="{MENTA_CLARO}" fill-opacity="0.85">OSINT · LINUX · TROPEIRO</text>
  <text x="132" y="{yb+120}" font-family="{TITULO},sans-serif" font-weight="800" font-size="150" letter-spacing="-4" fill="url(#wm)">TOCAIA</text>
  <line x1="140" y1="{yb+150}" x2="700" y2="{yb+150}" stroke="{MENTA}" stroke-opacity="0.6"/>
  <text x="140" y="{yb+192}" font-family="{MONO},monospace" font-size="17" letter-spacing="3" fill="{TEXTO}" fill-opacity="0.92">LEIA O PADRÃO · OUÇA O SILÊNCIO · <tspan fill="{MENTA}">POSICIONE-SE E ESPERE</tspan></text>""" if titulo else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs>
    <linearGradient id="wm" x1="0" x2="1"><stop offset="0" stop-color="{MENTA_CLARO}"/><stop offset="1" stop-color="{MENTA_ESCURO}"/></linearGradient>
    <linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{FUNDO}" stop-opacity="0.55"/>
      <stop offset="0.35" stop-color="{FUNDO}" stop-opacity="0.05"/>
      <stop offset="0.72" stop-color="{FUNDO}" stop-opacity="0.25"/>
      <stop offset="1" stop-color="{FUNDO}" stop-opacity="0.85"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="{FUNDO}"/>
  <image xlink:href="data:image/png;base64,{foto_b64}" x="0" y="0" width="1920" height="1080" preserveAspectRatio="xMidYMid slice"/>
  <rect width="1920" height="1080" fill="url(#scrim)"/>{bloco}
  <text x="140" y="1020" font-family="{MONO},monospace" font-size="13" letter-spacing="4" fill="{APAGADO}" fill-opacity="0.8">DEIVOSINT · OSINT NO JUTSU</text>
</svg>
"""


def main(destino=None):
    inc = Path(destino) if destino else RAIZ / "iso" / "config" / "includes.chroot"
    bg = inc / "usr/share/backgrounds/tocaia"
    bg.mkdir(parents=True, exist_ok=True)

    espreita = Image.open(MARCA / "tocaia-espreita.png").convert("RGB")
    face = Image.open(MARCA / "tocaia-face.png").convert("RGB")
    face_marca = Image.open(MARCA / "tocaia-face-marca.png").convert("RGB")

    # preserva o wallpaper vetorial original (se já gerado) como 'tocaia-mira.svg'
    orig = bg / "tocaia.svg"
    if orig.exists():
        (bg / "tocaia-mira.svg").write_text(orig.read_text(encoding="utf-8"), encoding="utf-8")

    # wallpaper principal = a onça na espreita (desktop E login apontam para tocaia.svg)
    (bg / "tocaia.svg").write_text(wallpaper_svg(b64(cobrir(espreita, 1920, 1080))), encoding="utf-8")
    (bg / "tocaia-face.svg").write_text(wallpaper_svg(b64(cobrir(face, 1920, 1080))), encoding="utf-8")

    # fundo de login com a face centralizada (opcional; o greeter pode apontar aqui)
    login = Image.new("RGB", (1920, 1080), tuple(int(FUNDO.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
    fm = face_marca.copy()
    esc = min(900 / fm.width, 820 / fm.height)
    fm = fm.resize((round(fm.width * esc), round(fm.height * esc)), Image.LANCZOS)
    login.paste(fm, ((1920 - fm.width) // 2, (1080 - fm.height) // 2 - 30))
    login.save(bg / "login.png")

    # ícone do app = a face (quadrada), em vários tamanhos
    lado = min(face.width, face.height)
    faceq = face.crop(((face.width - lado) // 2, 0, (face.width - lado) // 2 + lado, lado))
    for tam in (16, 22, 24, 32, 48, 64, 128, 256):
        dest = inc / f"usr/share/icons/hicolor/{tam}x{tam}/apps"
        dest.mkdir(parents=True, exist_ok=True)
        faceq.resize((tam, tam), Image.LANCZOS).save(dest / "tocaia.png")
    pix = inc / "usr/share/pixmaps"
    pix.mkdir(parents=True, exist_ok=True)
    faceq.resize((256, 256), Image.LANCZOS).save(pix / "tocaia.png")

    print(f"marca aplicada: wallpaper (onça), face, login e ícones em {inc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os recursos visuais fotográficos da TOCAIA a partir das artes da marca
(a onça na espreita e a face de olhos ciano), casando-as com a paleta do tema.

    python3 assets/gerar_marca.py            # escreve em assets/gerado/
    python3 assets/gerar_marca.py --destino DIR

Produz:
  wallpaper-espreita.svg   wallpaper principal: a onça + wordmark TOCAIA
  wallpaper-face.svg       variante: a face de olhos ciano + wordmark
  login.svg                fundo da tela de login (LightDM)
  grub.png                 fundo do menu de boot (escurecido)
  plymouth/*.png           splash de boot (face centralizada)
  icones/tocaia-face-*.png ícones do app derivados da face (32..256)

Os .svg embutem a foto em base64 e desenham o wordmark por cima (o chroot da ISO
rasteriza com rsvg-convert; o tema continua vindo de tema/tokens.json).
Só biblioteca padrão + Pillow (para recortar/escalar as fotos e gerar ícones).
"""
import argparse
import base64
import json
from pathlib import Path

from PIL import Image, ImageEnhance

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
T = json.loads((RAIZ / "tema" / "tokens.json").read_text(encoding="utf-8"))
MARCA = AQUI / "marca"


def b64(img, fmt="PNG"):
    import io
    buf = io.BytesIO()
    img.save(buf, format=fmt, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def cobrir(img, larg, alt):
    """Escala a imagem para cobrir larg×alt (como background-size:cover) e corta ao centro."""
    r = max(larg / img.width, alt / img.height)
    novo = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    x = (novo.width - larg) // 2
    y = (novo.height - alt) // 2
    return novo.crop((x, y, x + larg, y + alt))


def wallpaper_svg(foto_b64, w, h, titulo=True):
    c = T
    ybase = int(h * 0.60)
    bloco_titulo = f"""
  <text x="140" y="{ybase - 36}" font-family="{c['fontes']['mono']},monospace" font-size="15" letter-spacing="7" fill="{c['menta_clara']}" fill-opacity="0.85">OSINT · LINUX · 1.0 TROPEIRO</text>
  <text x="132" y="{ybase + 120}" font-family="{c['fontes']['titulo']},sans-serif" font-weight="800" font-size="150" letter-spacing="-4" fill="url(#wm)">TOCAIA</text>
  <line x1="140" y1="{ybase + 150}" x2="700" y2="{ybase + 150}" stroke="{c['menta']}" stroke-opacity="0.6"/>
  <text x="140" y="{ybase + 192}" font-family="{c['fontes']['mono']},monospace" font-size="17" letter-spacing="3" fill="{c['texto_claro']}" fill-opacity="0.92">LEIA O PADRÃO · OUÇA O SILÊNCIO · <tspan fill="{c['menta']}">POSICIONE-SE E ESPERE</tspan></text>""" if titulo else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="wm" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{c['menta_clara']}"/><stop offset="0.55" stop-color="{c['menta']}"/><stop offset="1" stop-color="{c['menta_escura']}"/>
    </linearGradient>
    <linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{c['fundo']}" stop-opacity="0.55"/>
      <stop offset="0.35" stop-color="{c['fundo']}" stop-opacity="0.05"/>
      <stop offset="0.72" stop-color="{c['fundo']}" stop-opacity="0.25"/>
      <stop offset="1" stop-color="{c['fundo']}" stop-opacity="0.85"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="{c['fundo']}"/>
  <image href="data:image/png;base64,{foto_b64}" xlink:href="data:image/png;base64,{foto_b64}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <rect width="{w}" height="{h}" fill="url(#scrim)"/>{bloco_titulo}
  <text x="140" y="{h - 60}" font-family="{c['fontes']['mono']},monospace" font-size="13" letter-spacing="4" fill="{c['apagado']}" fill-opacity="0.8">DEIVOSINT · OSINT NO JUTSU</text>
</svg>
"""


def gerar(destino):
    destino = Path(destino)
    (destino / "icones").mkdir(parents=True, exist_ok=True)
    (destino / "plymouth").mkdir(parents=True, exist_ok=True)

    espreita = Image.open(MARCA / "tocaia-espreita.png").convert("RGB")
    face = Image.open(MARCA / "tocaia-face.png").convert("RGB")
    face_marca = Image.open(MARCA / "tocaia-face-marca.png").convert("RGB")

    # --- wallpaper principal: a espreita (1920x1080) ---
    wp = cobrir(espreita, 1920, 1080)
    (destino / "wallpaper-espreita.svg").write_text(wallpaper_svg(b64(wp), 1920, 1080), encoding="utf-8")
    wp.save(destino / "wallpaper-espreita-base.png")  # versão sem texto (fallback)

    # --- wallpaper variante: a face ---
    wf = cobrir(face, 1920, 1080)
    (destino / "wallpaper-face.svg").write_text(wallpaper_svg(b64(wf), 1920, 1080), encoding="utf-8")

    # --- login: a face com a marca, centralizada sobre fundo escuro ---
    login = Image.new("RGB", (1920, 1080), tuple(int(T["fundo"][i:i+2], 16) for i in (1, 3, 5)))
    fm = face_marca.copy()
    escala = min(900 / fm.width, 820 / fm.height)
    fm = fm.resize((round(fm.width * escala), round(fm.height * escala)), Image.LANCZOS)
    login.paste(fm, ((1920 - fm.width) // 2, (1080 - fm.height) // 2 - 30))
    (destino / "login.svg").write_text(wallpaper_svg(b64(cobrir(espreita, 1920, 1080)), 1920, 1080, titulo=False), encoding="utf-8")
    login.save(destino / "login.png")

    # --- GRUB: espreita escurecida (o texto do tema do grub vai por cima) ---
    grub = ImageEnhance.Brightness(cobrir(espreita, 1920, 1080)).enhance(0.45)
    grub = ImageEnhance.Contrast(grub).enhance(0.9)
    grub.save(destino / "grub.png")

    # --- Plymouth: a face limpa, quadrada, centralizada ---
    lado = min(face.width, face.height)
    faceq = face.crop(((face.width - lado) // 2, 0, (face.width - lado) // 2 + lado, lado))
    faceq.resize((420, 420), Image.LANCZOS).save(destino / "plymouth" / "tocaia-face.png")

    # --- ícones do app derivados da face ---
    for tam in (16, 22, 24, 32, 48, 64, 128, 256):
        faceq.resize((tam, tam), Image.LANCZOS).save(destino / "icones" / f"tocaia-face-{tam}.png")

    print(f"✓ marca gerada em {destino}")
    return destino


def main(argv=None):
    p = argparse.ArgumentParser(description="Gera wallpapers/ícones/boot a partir das artes da marca.")
    p.add_argument("--destino", default=str(AQUI / "gerado"))
    a = p.parse_args(argv)
    gerar(a.destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

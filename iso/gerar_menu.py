#!/usr/bin/env python3
"""Gera o menu do Xfce agrupado pelas FASES da TOCAIA, não por tipo de tool.

Lê catalogo.json e escreve, dentro da árvore do live-build:
  usr/share/applications/tocaia-<tool>.desktop    um atalho por tool
  usr/share/desktop-directories/tocaia-<fase>.directory
  etc/xdg/menus/applications-merged/tocaia.menu   submenu "TOCAIA" com as 6 fases

    python3 iso/gerar_menu.py [pasta_destino]
"""
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FASES = ["Traçar", "Observar", "Cercar", "Aguardar", "Interpretar", "Atribuir"]


def slug(texto):
    """'Traçar' -> 'Tracar' (categorias de .desktop precisam ser ASCII)."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def gerar(catalogo, raiz):
    apps = raiz / "usr/share/applications"
    dirs = raiz / "usr/share/desktop-directories"
    menus = raiz / "etc/xdg/menus/applications-merged"
    for pasta in (apps, dirs, menus):
        pasta.mkdir(parents=True, exist_ok=True)

    for nome, t in catalogo.items():
        if t["fase"] not in FASES:
            raise ValueError(f"{nome}: fase inválida '{t['fase']}'")
        (apps / f"tocaia-{nome}.desktop").write_text(
            "[Desktop Entry]\nType=Application\n"
            f"Name={nome.upper()}\nComment={t['desc']}\n"
            f"Exec=xfce4-terminal --hold -T 'trem {nome}' -x trem {nome} --help\n"
            "Icon=utilities-terminal\nTerminal=false\n"
            f"Categories=X-TOCAIA-{slug(t['fase'])};\n",
            encoding="utf-8")

    blocos = []
    for i, fase in enumerate(FASES, 1):
        s = slug(fase)
        (dirs / f"tocaia-{s}.directory").write_text(
            f"[Desktop Entry]\nType=Directory\nName={i}. {fase}\nIcon=folder\n",
            encoding="utf-8")
        blocos.append(
            f"    <Menu><Name>TOCAIA-{s}</Name><Directory>tocaia-{s}.directory</Directory>\n"
            f"      <Include><Category>X-TOCAIA-{s}</Category></Include></Menu>")
    (dirs / "tocaia.directory").write_text(
        "[Desktop Entry]\nType=Directory\nName=TOCAIA\nIcon=applications-internet\n",
        encoding="utf-8")
    (menus / "tocaia.menu").write_text(
        '<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"\n'
        ' "http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">\n'
        "<Menu><Name>Applications</Name>\n"
        "  <Menu><Name>TOCAIA</Name><Directory>tocaia.directory</Directory>\n"
        + "\n".join(blocos) +
        "\n    <Layout>" + "".join(f"<Menuname>TOCAIA-{slug(f)}</Menuname>" for f in FASES) +
        "</Layout>\n  </Menu>\n</Menu>\n",
        encoding="utf-8")
    return len(catalogo)


def main(destino=None):
    catalogo = json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))
    raiz = Path(destino) if destino else RAIZ / "iso" / "config" / "includes.chroot"
    n = gerar(catalogo, raiz)
    print(f"menu gerado: {n} atalhos em 6 fases")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))

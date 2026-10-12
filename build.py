#!/usr/bin/env python3
"""Empacota cada pasta de tools/ como um .pyz em dist/. Só stdlib.

    python3 build.py           empacota tudo
    python3 build.py placar    empacota só uma
"""
import sys
import zipapp
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TOOLS, DIST = RAIZ / "tools", RAIZ / "dist"


def empacotar(pasta):
    if not (pasta / "__main__.py").exists():
        print(f"pulei {pasta.name}: sem __main__.py")
        return None
    destino = DIST / f"{pasta.name}.pyz"
    zipapp.create_archive(pasta, destino, interpreter="/usr/bin/env python3",
                          filter=lambda p: "__pycache__" not in p.parts)
    print(f"ok  {destino.relative_to(RAIZ)}")
    return destino


def main(nomes):
    DIST.mkdir(exist_ok=True)
    pastas = [TOOLS / n for n in nomes] if nomes else sorted(p for p in TOOLS.iterdir() if p.is_dir())
    feitos = [empacotar(p) for p in pastas]
    return 0 if all(feitos) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

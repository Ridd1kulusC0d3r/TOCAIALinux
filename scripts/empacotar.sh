#!/usr/bin/env bash
# Empacota cada ferramenta própria (pasta com __main__.py) como zipapp .pyz.
# Resultado: ferramentas/<nome>.pyz — um arquivo que roda em qualquer python3.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ/ferramentas"
feitos=0
for dir in */; do
  nome="${dir%/}"
  [ -f "$nome/__main__.py" ] || continue
  python3 -m zipapp "$nome" -o "$nome.pyz" -p "/usr/bin/env python3"
  printf '  \033[38;2;94;230;196m✓\033[0m %s.pyz\n' "$nome"
  feitos=$((feitos+1))
done
echo "$feitos ferramenta(s) empacotada(s)."

#!/bin/sh
# Dois cliques (ou: sh iniciar.sh). Empacota, testa e roda a demonstração.
cd "$(dirname "$0")" || exit 1
PY=$(command -v python3 || command -v python) || { echo "Instale o Python 3 em python.org"; read _; exit 1; }
"$PY" build.py && "$PY" -m unittest discover -s testes && \
"$PY" trem/trem.py && \
"$PY" trem/trem.py placar wargames/cenarios/rodada1-tropeiro-x-atalaia.json wargames/demo/alerts-demo.json --relatorio placar.md
echo; echo "Relatório salvo em placar.md. Aperte Enter para fechar."; read _

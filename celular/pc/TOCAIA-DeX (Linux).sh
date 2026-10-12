#!/bin/sh
# TOCAIA "Matula" - o PC como tela do celular. Dois cliques (ou: sh "TOCAIA-DeX (Linux).sh").
cd "$(dirname "$0")"
python3 tocaia_pc.py
printf "Enter para fechar..."; read -r _

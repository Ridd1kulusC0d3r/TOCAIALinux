#!/bin/bash
# TOCAIA "Matula" - o PC como tela do celular. Dois cliques (1ª vez: botão direito > Abrir).
cd "$(dirname "$0")"
python3 tocaia_pc.py
read -r -p "Enter para fechar..."

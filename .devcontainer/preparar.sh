#!/usr/bin/env bash
# Prepara o Codespace: empacota as ferramentas e deixa o `trem` no PATH.
set -e
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

# monta um TOCAIA_HOME dentro do workspace
mkdir -p opt-tocaia/ferramentas
cp catalogo/catalogo.json opt-tocaia/catalogo.json
cp -r casos opt-tocaia/casos
bash scripts/empacotar.sh
cp ferramentas/*.pyz opt-tocaia/ferramentas/ 2>/dev/null || true

# trem no PATH do usuário
mkdir -p "$HOME/.local/bin"
cp trem/trem.py "$HOME/.local/bin/trem"
chmod +x "$HOME/.local/bin/trem"
ln -sf "$HOME/.local/bin/trem" "$HOME/.local/bin/tocaia"

grep -q 'TOCAIA_SAUDOU' "$HOME/.bashrc" 2>/dev/null || cat >> "$HOME/.bashrc" <<'EOF'

# TOCAIA
export PATH="$HOME/.local/bin:$PATH"
export TOCAIA_HOME="/workspaces/TOCAIALinux/opt-tocaia"
export TOCAIA_EDICAO=nuvem
if [ -t 1 ] && [ -z "$TOCAIA_SAUDOU" ]; then export TOCAIA_SAUDOU=1; trem saudacao 2>/dev/null; fi
EOF

echo "Codespace pronto. Abra um terminal e rode:  trem"

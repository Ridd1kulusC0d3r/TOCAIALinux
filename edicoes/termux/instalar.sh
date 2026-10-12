#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# TOCAIA OSINT Linux — edição Termux (ARM64 nativo, para celular Android)
#
# Roda a TOCAIA de linha de comando direto no seu Poco X6 Pro (ou qualquer
# Android ARM64), SEM root e SEM baremetal. É o jeito prático de ter o `trem`
# no bolso. Veja o README desta pasta para o porquê de não ser baremetal.
#
#   pkg install git python
#   git clone https://github.com/Ridd1kulusC0d3r/TOCAIALinux
#   bash TOCAIALinux/edicoes/termux/instalar.sh
# =============================================================================
set -eu

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
DESTINO="$PREFIX/opt/tocaia"

msg(){ printf '\033[38;2;94;230;196m◆ %s\033[0m\n' "$*"; }

msg "1/4 · dependências (python e git)"
if command -v pkg >/dev/null; then
  pkg install -y python git >/dev/null 2>&1 || true
fi
command -v python3 >/dev/null || { echo "instale o python: pkg install python"; exit 1; }

msg "2/4 · validando e empacotando as ferramentas"
python3 "$RAIZ/trem/trem.py" validar
bash "$RAIZ/scripts/empacotar.sh"

msg "3/4 · instalando em $DESTINO"
mkdir -p "$DESTINO/ferramentas"
cp "$RAIZ/catalogo/catalogo.json" "$DESTINO/catalogo.json"
cp "$RAIZ"/ferramentas/*.pyz "$DESTINO/ferramentas/" 2>/dev/null || true
cp -r "$RAIZ/casos" "$DESTINO/casos"
cp -r "$RAIZ/wargames" "$DESTINO/wargames" 2>/dev/null || true
install -m 0755 "$RAIZ/trem/trem.py" "$PREFIX/bin/trem"
ln -sf "$PREFIX/bin/trem" "$PREFIX/bin/tocaia"

# edição = nuvem (sem apt/apk; dicas de terceiros apontam para pip/pkg)
cat > "$DESTINO/../etc/tocaia-release" <<EOF
NOME="TOCAIA OSINT Linux"
VERSAO="1.0"
CODINOME="Tropeiro"
EDICAO=termux
BASE="Termux (Android ARM64)"
EOF

msg "4/4 · saudação no terminal"
RC="$HOME/.bashrc"
grep -q TOCAIA_SAUDOU "$RC" 2>/dev/null || cat >> "$RC" <<EOF

# TOCAIA
export TOCAIA_HOME="$DESTINO"
export TOCAIA_EDICAO=termux
if [ -t 1 ] && [ -z "\${TOCAIA_SAUDOU:-}" ]; then export TOCAIA_SAUDOU=1; trem saudacao 2>/dev/null; fi
EOF

export TOCAIA_HOME="$DESTINO"
echo
TOCAIA_HOME="$DESTINO" trem saudacao || true
echo
msg "pronto! abra um novo terminal (ou 'source ~/.bashrc') e rode:  trem"
echo "    trem relogio --demo   ·   trem silencio <alerts.json>   ·   trem opsec"

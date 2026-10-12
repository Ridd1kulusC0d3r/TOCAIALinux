#!/usr/bin/env bash
# =============================================================================
# TOCAIA OSINT Linux — edição Raspberry Pi (baremetal ARM64)
#
# Transforma um Raspberry Pi OS (64-bit) recém-gravado numa TOCAIA. Este é o
# caminho de BAREMETAL ARM que realmente funciona: o Pi boota do cartão SD,
# com a TOCAIA rodando no metal.
#
#   sudo ./edicoes/raspberry/instalar.sh            # só o trem (Pi OS Lite)
#   sudo ./edicoes/raspberry/instalar.sh --desktop  # + tema (Pi OS com desktop)
#
# Roda NO próprio Pi, depois do primeiro boot. Para Pi 3/4/5 (arm64).
# =============================================================================
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
COM_DESKTOP=0
[ "${1:-}" = "--desktop" ] && COM_DESKTOP=1
msg(){ printf '\033[38;2;94;230;196m◆ %s\033[0m\n' "$*"; }
[ "$(id -u)" -eq 0 ] || { echo "rode com sudo"; exit 1; }

ARQ="$(dpkg --print-architecture 2>/dev/null || uname -m)"
case "$ARQ" in arm64|aarch64) :;; *) echo "aviso: isto é para arm64; detectei $ARQ";; esac

msg "1/4 · pacotes base"
apt-get update
apt-get install -y python3 python3-venv git whois dnsutils libimage-exiftool-perl ca-certificates

msg "2/4 · empacotando e instalando o trem"
python3 "$RAIZ/trem/trem.py" validar
bash "$RAIZ/scripts/empacotar.sh"
install -d /opt/tocaia/ferramentas
cp "$RAIZ/catalogo/catalogo.json" /opt/tocaia/catalogo.json
cp "$RAIZ"/ferramentas/*.pyz /opt/tocaia/ferramentas/
cp -r "$RAIZ/casos" /opt/tocaia/casos
cp -r "$RAIZ/wargames" /opt/tocaia/wargames 2>/dev/null || true
install -m 0755 "$RAIZ/trem/trem.py" /usr/local/bin/trem
ln -sf /usr/local/bin/trem /usr/local/bin/tocaia
cat > /etc/tocaia-release <<EOF
NOME="TOCAIA OSINT Linux"
VERSAO="1.0"
CODINOME="Tropeiro"
EDICAO=debian
BASE="Raspberry Pi OS (arm64)"
EOF

msg "3/4 · saudação no terminal"
cat > /etc/profile.d/tocaia.sh <<'EOF'
case $- in *i*)
  if [ -z "${TOCAIA_SAUDOU:-}" ] && command -v trem >/dev/null; then
    export TOCAIA_SAUDOU=1; trem saudacao 2>/dev/null || true
  fi
;; esac
EOF

if [ "$COM_DESKTOP" -eq 1 ]; then
  msg "4/4 · tema (desktop do Pi OS)"
  if ! python3 -c "import PIL" 2>/dev/null; then apt-get install -y python3-pil || true; fi
  python3 "$RAIZ/assets/gerar_marca.py" --destino /tmp/marca 2>/dev/null || true
  python3 "$RAIZ/tema/gerar_tema.py" --destino / || true
  # wallpaper no PIXEL/labwc: aponta para o nosso (se o conversor existir)
  command -v rsvg-convert >/dev/null && [ -f /usr/share/tocaia/wallpaper.svg ] && \
    rsvg-convert -w 1920 -h 1080 /usr/share/tocaia/wallpaper.svg -o /usr/share/tocaia/wallpaper.png || true
  echo "   dica: Preferências → Aparência → Papel de parede → /usr/share/tocaia/wallpaper.png"
else
  msg "4/4 · pronto (modo terminal)"
fi

echo
trem saudacao || true
echo
msg "feito. Abra um novo terminal e rode:  trem"

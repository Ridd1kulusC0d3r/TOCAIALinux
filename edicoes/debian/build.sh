#!/usr/bin/env bash
# =============================================================================
# TOCAIA OSINT Linux — construtor da ISO (edição Debian + Xfce, via live-build)
#
#   sudo ./edicoes/debian/build.sh
#
# Precisa de: Debian/Ubuntu com os pacotes 'live-build' e 'git' e acesso à
# internet (baixa os pacotes do Debian). Roda como root (o live-build exige).
# Gera: dist/TOCAIA-OSINT-Linux-1.0-Tropeiro-amd64.iso
#
# O que este script faz, em ordem:
#   1. valida o catálogo e empacota as ferramentas .pyz;
#   2. gera o tema (tema/gerar_tema.py) direto dentro de config/includes.chroot;
#   3. copia o lançador 'trem', o catálogo e as ferramentas para a ISO;
#   4. chama 'lb build', que monta o sistema e fecha o ISO híbrido (BIOS+UEFI).
# =============================================================================
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
VERSAO="1.0"
CODINOME="Tropeiro"
ARQ="amd64"
ISO="TOCAIA-OSINT-Linux-${VERSAO}-${CODINOME}-${ARQ}.iso"

info(){ printf '\033[38;2;94;230;196m◆ %s\033[0m\n' "$*"; }
erro(){ printf '\033[38;2;229;122;107m✗ %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || erro "rode como root (sudo)."
command -v lb >/dev/null || erro "live-build não encontrado. Instale: apt install live-build"

cd "$AQUI"

info "1/5 · validando catálogo e empacotando ferramentas (.pyz)"
python3 "$RAIZ/trem/trem.py" validar
bash "$RAIZ/scripts/empacotar.sh"

info "2/5 · limpando build anterior (preserva listas e hooks versionados)"
lb clean >/dev/null 2>&1 || true
# só o que é GERADO entra de novo a cada build; as pastas versionadas ficam
rm -rf config/includes.chroot/opt/tocaia \
       config/includes.chroot/usr/share/themes/TOCAIA \
       config/includes.chroot/usr/share/tocaia \
       config/includes.chroot/usr/local/bin/trem

info "3/5 · configurando o live-build"
# auto/config é lido pelo 'lb config'; ele cria os arquivos auto sem apagar
# config/package-lists, config/hooks e config/includes.chroot (nosso conteúdo)
lb config

# ---- material da TOCAIA dentro da ISO -------------------------------------
PAYLOAD="config/includes.chroot/opt/tocaia"
mkdir -p "$PAYLOAD/ferramentas" "config/includes.chroot/usr/local/bin"
cp "$RAIZ/catalogo/catalogo.json"            "$PAYLOAD/catalogo.json"
cp "$RAIZ/ferramentas/"*.pyz                 "$PAYLOAD/ferramentas/" 2>/dev/null || true
cp -r "$RAIZ/casos"                          "$PAYLOAD/casos"
cp "$RAIZ/trem/trem.py"                      "config/includes.chroot/usr/local/bin/trem"
chmod +x "config/includes.chroot/usr/local/bin/trem"

info "4/5 · gerando marca (onça/face) e tema (GTK, janelas, wallpaper, menu, login)"
# as artes fotográficas são geradas a partir de assets/marca (precisa de Pillow)
if ! python3 -c "import PIL" 2>/dev/null; then
  python3 -m pip install --quiet --break-system-packages pillow 2>/dev/null || \
    apt-get install -y python3-pil 2>/dev/null || true
fi
if python3 -c "import PIL" 2>/dev/null; then
  python3 "$RAIZ/assets/gerar_marca.py" --destino "$RAIZ/assets/gerado"
else
  echo "   (Pillow indisponível — a distro usará o wallpaper vetorial e o losango como ícone)"
fi
python3 "$RAIZ/tema/gerar_tema.py" --destino "config/includes.chroot"
# wallpaper em PNG (o live-build roda num Debian com rsvg; convertido no hook 0040)

# manual ilustrado e docs vão para dentro da ISO
mkdir -p "config/includes.chroot/usr/share/tocaia/manual"
cp -r "$RAIZ/docs/manual/." "config/includes.chroot/usr/share/tocaia/manual/" 2>/dev/null || true
cp "$RAIZ/COMECE-AQUI.md" "config/includes.chroot/usr/share/tocaia/" 2>/dev/null || true

info "5/5 · lb build (isto baixa pacotes do Debian e leva vários minutos)"
lb build 2>&1 | tee "$RAIZ/dist-build.log"

mkdir -p "$RAIZ/dist"
if [ -f "live-image-${ARQ}.hybrid.iso" ]; then
  mv "live-image-${ARQ}.hybrid.iso" "$RAIZ/dist/$ISO"
  ( cd "$RAIZ/dist" && sha256sum "$ISO" > "$ISO.sha256" )
  info "pronto: dist/$ISO"
  ls -lh "$RAIZ/dist/$ISO"
else
  erro "a ISO não foi gerada — veja dist-build.log"
fi

#!/bin/sh
# Constrói a ISO live da TOCAIA. Precisa de Debian/Ubuntu com live-build, como root.
#   sudo apt install live-build
#   sudo ./iso/construir-iso.sh
# Ou sem instalar nada: o workflow .github/workflows/iso.yml faz isto na nuvem.
set -eu
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
INC="$RAIZ/iso/config/includes.chroot"

echo "== 1/4 empacotando as tools"
python3 "$RAIZ/build.py"

echo "== 2/4 copiando a distro para dentro da ISO"
mkdir -p "$INC/opt/tocaia/dist" "$INC/usr/local/bin" "$INC/etc/profile.d"
cp "$RAIZ"/dist/*.pyz "$INC/opt/tocaia/dist/"
cp "$RAIZ/catalogo.json" "$INC/opt/tocaia/"
cp -r "$RAIZ/wargames" "$INC/opt/tocaia/"
cp "$RAIZ/trem/trem.py" "$INC/usr/local/bin/trem"
cp "$RAIZ/container/tocaia-profile.sh" "$INC/etc/profile.d/tocaia.sh"

echo "== 3/4 gerando tema e menu por fases"
python3 "$RAIZ/tema/gerar_tema.py" "$INC"
python3 "$RAIZ/iso/gerar_menu.py" "$INC"

# marca fotográfica (onça/face): sobrepõe o wallpaper, instala a face como ícone
if ! python3 -c "import PIL" 2>/dev/null; then
  python3 -m pip install --quiet --break-system-packages pillow 2>/dev/null || \
    apt-get install -y python3-pil 2>/dev/null || true
fi
if python3 -c "import PIL" 2>/dev/null; then
  python3 "$RAIZ/assets/gerar_marca.py" "$INC"
else
  echo "   (Pillow indisponível — mantendo o wallpaper vetorial)"
fi

echo "== 4/4 live-build"
cd "$RAIZ/iso"
lb clean --purge >/dev/null 2>&1 || true
lb config
lb build
ls -lh "$RAIZ"/iso/*.iso

#!/usr/bin/env bash
# Constrói a imagem Alpine da TOCAIA e, opcionalmente, exporta um rootfs para WSL.
#
#   ./edicoes/alpine/build.sh                 # imagem local (arquitetura atual)
#   ./edicoes/alpine/build.sh --multi         # amd64 + arm64 (precisa de buildx)
#   ./edicoes/alpine/build.sh --wsl           # também gera dist/TOCAIA-WSL.tar.gz
#
# O contexto de build é a RAIZ do repositório (o Dockerfile usa caminhos de lá).
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKERFILE="$RAIZ/edicoes/alpine/Dockerfile"
TAG="tocaia:1.0"
cd "$RAIZ"

info(){ printf '\033[38;2;94;230;196m◆ %s\033[0m\n' "$*"; }

info "validando catálogo e empacotando ferramentas"
python3 trem/trem.py validar
bash scripts/empacotar.sh

modo="local"; wsl=0
for a in "$@"; do
  [ "$a" = "--multi" ] && modo="multi"
  [ "$a" = "--wsl" ] && wsl=1
done

if [ "$modo" = "multi" ]; then
  info "build multi-arquitetura (amd64 + arm64)"
  docker buildx build --platform linux/amd64,linux/arm64 -f "$DOCKERFILE" -t "$TAG" .
else
  info "build local"
  docker build -f "$DOCKERFILE" -t "$TAG" .
fi

if [ "$wsl" -eq 1 ]; then
  info "exportando rootfs para WSL"
  mkdir -p "$RAIZ/dist"
  cid=$(docker create "$TAG")
  docker export "$cid" | gzip > "$RAIZ/dist/TOCAIA-WSL.tar.gz"
  docker rm "$cid" >/dev/null
  info "pronto: dist/TOCAIA-WSL.tar.gz"
  echo "   No Windows:  wsl --import TOCAIA C:\\WSL\\TOCAIA dist\\TOCAIA-WSL.tar.gz"
  echo "                wsl -d TOCAIA"
fi

info "imagem pronta: $TAG"
echo "   docker run --rm -it $TAG"

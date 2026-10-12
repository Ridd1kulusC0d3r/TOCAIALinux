#!/bin/bash
# TOCAIA OSINT Linux — lançador de dois cliques (macOS).
# Precisa do Docker Desktop instalado e aberto.
# Dica: na primeira vez, clique com o botão direito > Abrir (Gatekeeper).
cd "$(dirname "$0")"
echo
echo "  ◆ TOCAIA OSINT Linux — uai, sô."
echo
if ! command -v docker >/dev/null; then
  echo "  [!] Docker não encontrado. Instale o Docker Desktop:"
  echo "      https://www.docker.com/products/docker-desktop/"
  read -r -p "  Enter para fechar..."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "  [!] Abra o Docker Desktop e espere ficar verde, depois rode de novo."
  read -r -p "  Enter para fechar..."
  exit 1
fi
mkdir -p "$HOME/TOCAIA-casos"
echo "  Abrindo a imagem (só demora na primeira vez)..."
echo
docker run --rm -it -v "$HOME/TOCAIA-casos:/home/analista/casos" ghcr.io/ridd1kulusc0d3r/tocaia:latest
read -r -p "  Enter para fechar..."

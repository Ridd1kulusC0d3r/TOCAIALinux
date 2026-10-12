#!/bin/sh
# Gera tocaia-wsl.tar a partir da imagem do container, para importar no WSL.
# Rode na raiz do repositório, numa máquina com Docker.
set -eu
docker build -f container/Dockerfile -t tocaia:tropeiro .
id=$(docker create tocaia:tropeiro)
docker export "$id" -o tocaia-wsl.tar
docker rm "$id" >/dev/null
echo "pronto: tocaia-wsl.tar"
echo "No Windows (PowerShell):"
echo "  wsl --import TOCAIA \$env:USERPROFILE\\TOCAIA .\\tocaia-wsl.tar"
echo "  wsl -d TOCAIA -u analista"

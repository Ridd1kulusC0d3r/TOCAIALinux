#!/bin/sh
# Sobe o Wazuh single-node oficial (wazuh-docker) para o war game.
# Uso:  sh wargames/lab/subir-lab.sh v4.X.Y
# Escolha a versão em https://github.com/wazuh/wazuh-docker/releases
# Requisitos: Docker com Compose, 8 GB de RAM livres, Linux/WSL2/macOS.
set -eu
VERSAO="${1:?informe a versão do wazuh-docker, ex.: sh subir-lab.sh v4.X.Y}"
DESTINO="${2:-$HOME/tocaia-lab}"

if [ "$(uname)" = "Linux" ]; then
  atual=$(sysctl -n vm.max_map_count 2>/dev/null || echo 0)
  [ "$atual" -ge 262144 ] || sudo sysctl -w vm.max_map_count=262144
fi

[ -d "$DESTINO" ] || git clone --depth 1 --branch "$VERSAO" https://github.com/wazuh/wazuh-docker.git "$DESTINO"
cd "$DESTINO/single-node"
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
echo
echo "Wazuh subindo. Painel: https://localhost (usuário e senha padrão no README do wazuh-docker; troque-os)."
echo "Depois instale o agente nas VMs alvo (win-lab-01, linux-lab-01) e siga wargames/README.md."

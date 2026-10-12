#!/bin/sh
# Copia o alerts.json do manager do Wazuh (container) para a pasta atual,
# já recortado para o período da rodada.
# Uso: sh wargames/lab/exportar-alertas.sh [nome_do_container]
set -eu
C="${1:-single-node-wazuh.manager-1}"
docker cp "$C":/var/ossec/logs/alerts/alerts.json ./alerts.json
echo "alerts.json copiado ($(wc -l < alerts.json) alertas). Agora:"
echo "  trem placar wargames/cenarios/rodada1-tropeiro-x-atalaia.json alerts.json --relatorio placar.md"

#!/usr/bin/env python3
"""Gera alertas SINTÉTICOS no formato do alerts.json do Wazuh para treinar o
placar e o silencio sem precisar subir o laboratório. Os IDs de regra 1009xx
são fictícios (faixa de regras customizadas), só para a demonstração.

Roteiro da demo (bate com a rodada 1):
  P1 detectado em 2 min · P2 detectado em 30 s · P3 e P4 passam batido
  P5 detectado em 1 min · P6 o win-lab-01 silencia (detecção pela ausência)
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

INICIO = datetime.fromisoformat("2026-10-12T13:00:00-03:00")
FIM = datetime.fromisoformat("2026-10-12T15:40:00-03:00")
APAGOU = datetime.fromisoformat("2026-10-12T15:15:00-03:00")


def alerta(quando, host, regra, desc, mitre=None, nivel=3):
    regra_obj = {"id": str(regra), "level": nivel, "description": desc}
    if mitre:
        regra_obj["mitre"] = {"id": [mitre]}
    return {"timestamp": quando.strftime("%Y-%m-%dT%H:%M:%S.000%z"),
            "agent": {"name": host}, "rule": regra_obj}


def main():
    eventos = []
    t = INICIO
    while t <= FIM:  # ruído de fundo: cada host fala a cada 2 minutos
        for host in ("win-lab-01", "linux-lab-01", "dc-lab-01"):
            if host == "win-lab-01" and t >= APAGOU:
                continue  # o adversário calou este host
            eventos.append(alerta(t, host, 100900, "demo: heartbeat de auditoria"))
        t += timedelta(minutes=2)
    base = datetime.fromisoformat
    eventos += [
        alerta(base("2026-10-12T14:02:00-03:00"), "win-lab-01", 100910,
               "demo: PowerShell com comando codificado", "T1059.001", 12),
        alerta(base("2026-10-12T14:15:30-03:00"), "win-lab-01", 100920,
               "demo: acesso à memória da LSASS", "T1003.001", 15),
        alerta(base("2026-10-12T15:01:00-03:00"), "linux-lab-01", 100930,
               "demo: usuário local criado", "T1136.001", 8),
    ]
    eventos.sort(key=lambda e: e["timestamp"])
    destino = Path(__file__).with_name("alerts-demo.json")
    destino.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in eventos),
                       encoding="utf-8")
    print(f"{len(eventos)} alertas sintéticos em {destino}")


if __name__ == "__main__":
    main()

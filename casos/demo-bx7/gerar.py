#!/usr/bin/env python3
"""
Gera o caso sintético #BX-7 (o mesmo sujeito dos slides 19 e 45 da masterclass).

Nenhuma pessoa real: os horários são inventados, com semente fixa, para que o
resultado seja sempre o mesmo (reprodutível = auditável).

Roteiro de 44 dias (fuso UTC-03:00):
  dias  0–21  linha de base: manhã 8–9h, almoço 12–13h, noite 19–21h; fim de semana madrugada e noite
  dias 22–27  pico anômalo (energy burst): o dobro de postagens
  dias 28–29  queda
  dias 30–36  silêncio total — "o silêncio tem data de início"
  dias 37–43  retorno, mais contido
"""
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

FUSO = timezone(timedelta(hours=-3))
INICIO = datetime(2026, 8, 3, tzinfo=FUSO)  # uma segunda-feira
rng = random.Random(7)  # BX-7


def horas_do_dia(data):
    if data.weekday() < 5:  # dias úteis
        return [8, 8, 9, 12, 13, 19, 20, 20, 21]
    return [0, 1, 12, 13, 20, 21, 22, 22, 23]


def postagens_no_dia(n):
    if n <= 21:
        return rng.randint(4, 6)
    if n <= 27:
        return rng.randint(10, 13)
    if n <= 29:
        return rng.randint(1, 2)
    if n <= 36:
        return 0
    return rng.randint(3, 4)


linhas = []
for n in range(44):
    dia = INICIO + timedelta(days=n)
    for _ in range(postagens_no_dia(n)):
        hora = rng.choice(horas_do_dia(dia))
        momento = dia.replace(hour=hora, minute=rng.randint(0, 59), second=rng.randint(0, 59))
        linhas.append(momento)
linhas.sort()

destino = Path(__file__).with_name("postagens.csv")
with destino.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "plataforma", "tipo"])
    for m in linhas:
        w.writerow([m.isoformat(), "rede-ficticia", "post"])
print(f"{len(linhas)} postagens sintéticas -> {destino}")

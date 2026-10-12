"""silencio — detecção pela ausência.

Lê eventos em JSON Lines (o alerts.json/archives.json do Wazuh já serve) e
aponta as fontes que ficaram quietas demais em relação ao próprio ritmo.
Quando o adversário apaga logs ou derruba o agente (ATT&CK T1070 / T1562),
a contagem cai, e o silêncio vira o sinal.

    trem silencio alerts.json
    trem silencio eventos.jsonl --fonte host --tempo ts --fator 4
    trem silencio alerts.json --agora 2026-10-12T15:00:00-03:00 --json

Regra: uma fonte está em silêncio quando o tempo desde o último evento
passa de FATOR vezes o intervalo mediano dela (e de um mínimo absoluto).
"""
import argparse
import json
import re
import statistics
import sys
from datetime import datetime, timezone


def pegar(evento, caminho):
    """Lê 'agent.name' de {'agent': {'name': ...}}."""
    atual = evento
    for parte in caminho.split("."):
        if not isinstance(atual, dict) or parte not in atual:
            return None
        atual = atual[parte]
    return atual


def para_data(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor, tz=timezone.utc)
    texto = str(valor).strip().replace("Z", "+00:00")
    texto = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", texto)  # -0300 -> -03:00
    data = datetime.fromisoformat(texto)
    return data if data.tzinfo else data.replace(tzinfo=timezone.utc)


def ler_eventos(linhas, campo_fonte, campo_tempo):
    por_fonte = {}
    for n, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha:
            continue
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            print(f"aviso: linha {n} não é JSON, pulei", file=sys.stderr)
            continue
        fonte, quando = pegar(ev, campo_fonte), para_data(pegar(ev, campo_tempo))
        if fonte is None or quando is None:
            continue
        por_fonte.setdefault(str(fonte), []).append(quando)
    return por_fonte


def analisar(por_fonte, agora=None, fator=5.0, minimo_s=300, min_eventos=5):
    if agora is None:
        agora = max(max(v) for v in por_fonte.values()) if por_fonte else None
    resultado = []
    for fonte, tempos in sorted(por_fonte.items()):
        tempos.sort()
        if len(tempos) < min_eventos:
            resultado.append({"fonte": fonte, "estado": "pouco dado", "eventos": len(tempos)})
            continue
        intervalos = [(b - a).total_seconds() for a, b in zip(tempos, tempos[1:])]
        mediana = max(statistics.median(intervalos), 1.0)
        lacuna = (agora - tempos[-1]).total_seconds()
        quieta = lacuna > fator * mediana and lacuna > minimo_s
        resultado.append({
            "fonte": fonte,
            "estado": "SILÊNCIO" if quieta else "normal",
            "eventos": len(tempos),
            "intervalo_mediano_s": round(mediana, 1),
            "sem_eventos_ha_s": round(lacuna, 1),
            "razao": round(lacuna / mediana, 1),
            "ultimo_evento": tempos[-1].isoformat(),
        })
    return resultado


def main(argv=None):
    p = argparse.ArgumentParser(prog="trem silencio", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("arquivo", help="JSON Lines; use - para ler da entrada padrão")
    p.add_argument("--fonte", default="agent.name", help="campo da fonte (padrão agent.name)")
    p.add_argument("--tempo", default="timestamp", help="campo de data (padrão timestamp)")
    p.add_argument("--fator", type=float, default=5.0, help="quantas vezes o ritmo normal")
    p.add_argument("--minimo", type=int, default=300, help="lacuna mínima em segundos")
    p.add_argument("--agora", help="referência de tempo (padrão: último evento do arquivo)")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    a = p.parse_args(argv)

    if a.arquivo == "-":
        por_fonte = ler_eventos(sys.stdin, a.fonte, a.tempo)
    else:
        with open(a.arquivo, encoding="utf-8") as f:
            por_fonte = ler_eventos(f, a.fonte, a.tempo)
    if not por_fonte:
        print("nenhum evento com os campos pedidos; confira --fonte e --tempo")
        return 2
    agora = para_data(a.agora) if a.agora else None
    r = analisar(por_fonte, agora, a.fator, a.minimo)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print(f"{'fonte':20} {'estado':11} {'eventos':>7} {'ritmo(s)':>9} {'quieta há(s)':>12} {'x':>6}")
        for x in r:
            print(f"{x['fonte']:20} {x['estado']:11} {x['eventos']:>7} "
                  f"{x.get('intervalo_mediano_s', '-'):>9} {x.get('sem_eventos_ha_s', '-'):>12} "
                  f"{x.get('razao', '-'):>6}")
    return 1 if any(x["estado"] == "SILÊNCIO" for x in r) else 0


if __name__ == "__main__":
    sys.exit(main())

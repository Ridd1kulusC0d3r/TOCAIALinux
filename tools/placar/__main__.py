"""placar — juiz do war game ataque x defesa sobre o Wazuh.

O time vermelho executa os passos de um cenário (Atomic Red Team, CALDERA
ou à mão) e o time azul defende com o Wazuh. O placar lê o cenário e os
alertas exportados do Wazuh (alerts.json) e decide, passo a passo, quem
pontuou:

  * azul pontua quando um alerta com a mesma técnica ATT&CK (ou uma regra
    listada no passo) aparece no host certo dentro da janela; ganha bônus
    por rapidez;
  * vermelho pontua quando o passo passa despercebido;
  * passos marcados com "deteccao": "ausencia" também valem para o azul se
    o host alvo SILENCIAR enquanto os outros continuam falando (o adversário
    apagou logs ou derrubou o agente).

    trem placar cenario.json alerts.json
    trem placar cenario.json alerts.json --relatorio placar.md
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone


def pegar(evento, caminho, padrao=None):
    atual = evento
    for parte in caminho.split("."):
        if not isinstance(atual, dict) or parte not in atual:
            return padrao
        atual = atual[parte]
    return atual


def para_data(valor):
    texto = str(valor).strip().replace("Z", "+00:00")
    texto = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", texto)
    data = datetime.fromisoformat(texto)
    return data if data.tzinfo else data.replace(tzinfo=timezone.utc)


def ler_alertas(caminho):
    alertas = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            ev = json.loads(linha)
            mitre = pegar(ev, "rule.mitre.id", []) or []
            alertas.append({
                "quando": para_data(pegar(ev, "timestamp")),
                "host": pegar(ev, "agent.name", ""),
                "regra": str(pegar(ev, "rule.id", "")),
                "mitre": [mitre] if isinstance(mitre, str) else list(mitre),
                "descricao": pegar(ev, "rule.description", ""),
            })
    return sorted(alertas, key=lambda a: a["quando"])


def tecnica_bate(pedida, vistas, aceitar_pai):
    for t in vistas:
        if t == pedida:
            return True
        if aceitar_pai and t.split(".")[0] == pedida.split(".")[0]:
            return True
    return False


def julgar_passo(passo, alertas, janela, aceitar_pai):
    inicio = para_data(passo["quando"])
    fim = inicio + timedelta(seconds=passo.get("janela_s", janela))
    regras = {str(r) for r in passo.get("regras", [])}
    for a in alertas:
        if not (inicio <= a["quando"] <= fim) or a["host"] != passo["alvo"]:
            continue
        if a["regra"] in regras or tecnica_bate(passo["tecnica"], a["mitre"], aceitar_pai):
            return {"detectado": True, "como": f"regra {a['regra']}: {a['descricao']}",
                    "mttd_s": (a["quando"] - inicio).total_seconds()}
    if passo.get("deteccao") == "ausencia":
        do_alvo = [a for a in alertas if a["host"] == passo["alvo"] and inicio < a["quando"] <= fim]
        outros = [a for a in alertas if a["host"] != passo["alvo"] and inicio < a["quando"] <= fim]
        if not do_alvo and outros:
            return {"detectado": True, "como": "pela ausência: o host silenciou",
                    "mttd_s": (outros[0]["quando"] - inicio).total_seconds()}
    return {"detectado": False, "como": "passou despercebido", "mttd_s": None}


def jogar(cenario, alertas):
    janela = cenario.get("janela_s", 600)
    aceitar_pai = cenario.get("aceitar_tecnica_pai", True)
    linhas, azul, vermelho = [], 0.0, 0.0
    for passo in cenario["passos"]:
        pontos = passo.get("pontos", 10)
        r = julgar_passo(passo, alertas, janela, aceitar_pai)
        if r["detectado"]:
            bonus = pontos * 0.5 * max(0.0, 1 - r["mttd_s"] / passo.get("janela_s", janela))
            azul += pontos + bonus
            ganho = ("azul", round(pontos + bonus, 1))
        else:
            vermelho += pontos
            ganho = ("vermelho", pontos)
        linhas.append({**passo, **r, "ponto_para": ganho[0], "pontos_ganhos": ganho[1]})
    detectados = [x for x in linhas if x["detectado"]]
    mttds = [x["mttd_s"] for x in detectados]
    return {
        "cenario": cenario.get("nome", "sem nome"),
        "passos": linhas,
        "azul": round(azul, 1),
        "vermelho": round(vermelho, 1),
        "cobertura_pct": round(100 * len(detectados) / len(linhas), 1) if linhas else 0.0,
        "mttd_medio_s": round(sum(mttds) / len(mttds), 1) if mttds else None,
        "vencedor": "azul" if azul > vermelho else "vermelho" if vermelho > azul else "empate",
        "lacunas": [x["tecnica"] for x in linhas if not x["detectado"]],
    }


def em_markdown(r):
    linhas = [f"# Placar — {r['cenario']}", "",
              f"**Vencedor:** {r['vencedor']} · azul {r['azul']} x vermelho {r['vermelho']} · "
              f"cobertura {r['cobertura_pct']}% · MTTD médio {r['mttd_medio_s']} s", "",
              "| Passo | Técnica | Host | Resultado | MTTD (s) | Ponto |",
              "|---|---|---|---|---|---|"]
    for x in r["passos"]:
        linhas.append(f"| {x['id']} {x.get('nome', '')} | {x['tecnica']} | {x['alvo']} | "
                      f"{x['como']} | {x['mttd_s'] if x['mttd_s'] is not None else '-'} | "
                      f"{x['ponto_para']} +{x['pontos_ganhos']} |")
    if r["lacunas"]:
        linhas += ["", "## Lacunas para a engenharia de detecção",
                   *[f"- {t}: escrever/ajustar regra e rejogar" for t in r["lacunas"]]]
    return "\n".join(linhas) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(prog="trem placar", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cenario", help="arquivo JSON do cenário")
    p.add_argument("alertas", help="alerts.json do Wazuh (JSON Lines)")
    p.add_argument("--relatorio", help="grava o placar em Markdown")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    a = p.parse_args(argv)
    with open(a.cenario, encoding="utf-8") as f:
        cenario = json.load(f)
    r = jogar(cenario, ler_alertas(a.alertas))
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False, default=str))
    else:
        print(em_markdown(r))
    if a.relatorio:
        with open(a.relatorio, "w", encoding="utf-8") as f:
            f.write(em_markdown(r))
        print(f"relatório gravado em {a.relatorio}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

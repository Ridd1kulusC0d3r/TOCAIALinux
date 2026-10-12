#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELÓGIO — "o relógio do alvo é um mapa".            DEIVOSINT · TOCAIA · fase T (Traçar)

Lê horários de postagens PÚBLICAS (um CSV com uma coluna de data/hora) e devolve:
  1. heatmap hora × dia da semana  (o padrão de vida)
  2. fuso horário provável         (pela janela de sono — sinal fraco)
  3. picos anômalos                (energy burst)
  4. silêncios anômalos            (o gap: "o silêncio tem data de início")
  5. indício de automação          ("humano tem ruído, bot tem relógio")

Cada achado sai com grau de confiança (A/M/B) e com "o que derrubaria" a
hipótese — perfil é hipótese, não sentença.

Uso:
  relogio postagens.csv
  relogio postagens.csv --fuso -03:00 --html relatorio.html --json achados.json
  relogio --demo        # roda com o caso sintético #BX-7

Só biblioteca padrão. Não acessa a internet: você traz os horários.
"""

import argparse
import csv
import hashlib
import html
import json
import math
import statistics
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

VERSAO = "1.0.0"
DIAS = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
COLUNAS_ACEITAS = ("timestamp", "data_hora", "datahora", "datetime", "data", "date", "created_at", "hora")


# ------------------------------------------------------------------ leitura

def ler_horarios(caminho):
    """Devolve (lista de datetimes em UTC, avisos). Aceita ISO 8601 e epoch."""
    avisos, horarios = [], []
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f)
        if not leitor.fieldnames:
            raise SystemExit("CSV vazio.")
        coluna = next((c for c in leitor.fieldnames if c.strip().lower() in COLUNAS_ACEITAS),
                      leitor.fieldnames[0])
        sem_fuso = 0
        for n, linha in enumerate(leitor, start=2):
            bruto = (linha.get(coluna) or "").strip()
            if not bruto:
                continue
            try:
                if bruto.replace(".", "", 1).isdigit():
                    dt = datetime.fromtimestamp(float(bruto), tz=timezone.utc)
                else:
                    dt = datetime.fromisoformat(bruto.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        sem_fuso += 1
                        dt = dt.replace(tzinfo=timezone.utc)
                horarios.append(dt.astimezone(timezone.utc))
            except ValueError:
                avisos.append(f"linha {n}: data ilegível '{bruto}' (ignorada)")
        if sem_fuso:
            avisos.append(f"{sem_fuso} horários sem fuso foram tratados como UTC — "
                          "confira a origem antes de concluir algo sobre o fuso.")
    horarios.sort()
    return horarios, avisos


def sha256_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def parse_fuso(texto):
    """'-03:00' -> timedelta(hours=-3)."""
    sinal = -1 if texto.startswith("-") else 1
    h, _, m = texto.lstrip("+-").partition(":")
    return timedelta(hours=sinal * int(h), minutes=sinal * int(m or 0))


def fmt_fuso(delta):
    minutos = int(delta.total_seconds() // 60)
    sinal = "-" if minutos < 0 else "+"
    return f"UTC{sinal}{abs(minutos) // 60:02d}:{abs(minutos) % 60:02d}"


# ------------------------------------------------------------------ análises

def histograma_horas(horarios, deslocamento=timedelta(0)):
    contagem = [0] * 24
    for dt in horarios:
        contagem[(dt + deslocamento).hour] += 1
    return contagem


def inferir_fuso(horarios):
    """Sinal fraco: a sequência de horas mais quieta do dia costuma ser o sono.

    Achamos o maior trecho contínuo (circular) de horas quase sem atividade em
    UTC e supomos que o meio dele cai por volta de 05h locais (a janela sem
    postagens costuma ir do adormecer até um pouco depois de acordar).
    Serve para levantar hipótese, nunca para cravar.
    """
    utc = histograma_horas(horarios)
    total = sum(utc) or 1
    limiar = 0.05 * total / 24  # "quase sem atividade"
    quietas = [v <= limiar for v in utc]
    melhor_inicio, melhor_tam = 0, 0
    if all(quietas):
        melhor_tam = 24
    else:
        for inicio in range(24):
            if not quietas[inicio] or quietas[(inicio - 1) % 24]:
                continue  # só começa onde a sequência começa
            tam = 0
            while tam < 24 and quietas[(inicio + tam) % 24]:
                tam += 1
            if tam > melhor_tam:
                melhor_inicio, melhor_tam = inicio, tam
    if melhor_tam == 0:  # nenhuma hora quieta: usa a janela de 6h de menor soma
        melhor_inicio = min(range(24), key=lambda i: sum(utc[(i + k) % 24] for k in range(6)))
        melhor_tam = 6
    meio_utc = melhor_inicio + melhor_tam / 2
    horas = math.floor(5.0 - meio_utc + 0.5)  # arredonda .5 para cima
    horas = (horas + 12) % 24 - 12  # normaliza para -12..+11
    soma_janela = sum(utc[(melhor_inicio + k) % 24] for k in range(melhor_tam))
    contraste = (soma_janela / melhor_tam) / (total / 24)
    confianca = "M" if contraste < 0.15 and melhor_tam >= 5 and total >= 100 else "B"
    return {
        "fuso": fmt_fuso(timedelta(hours=horas)),
        "deslocamento_horas": horas,
        "janela_quieta_utc": f"{melhor_inicio:02d}h–{(melhor_inicio + melhor_tam) % 24:02d}h",
        "horas_quietas": melhor_tam,
        "contraste": round(contraste, 3),
        "confianca": confianca,
    }


def heatmap(horarios, deslocamento):
    grade = [[0] * 24 for _ in range(7)]
    for dt in horarios:
        local = dt + deslocamento
        grade[local.weekday()][local.hour] += 1
    return grade


def serie_diaria(horarios, deslocamento):
    dias = Counter((dt + deslocamento).date() for dt in horarios)
    if not dias:
        return []
    inicio, fim = min(dias), max(dias)
    serie, d = [], inicio
    while d <= fim:
        serie.append((d, dias.get(d, 0)))
        d += timedelta(days=1)
    return serie


def mad(valores, mediana):
    return statistics.median(abs(v - mediana) for v in valores) or 1.0


def detectar_picos(serie):
    """Z-score robusto (mediana/MAD), agrupando dias seguidos num só episódio."""
    valores = [v for _, v in serie]
    if len(valores) < 7:
        return []
    med = statistics.median(valores)
    desvio = mad(valores, med) * 1.4826
    episodios, atual = [], []
    for d, v in serie + [(None, 0)]:
        anomalo = d is not None and (v - med) / desvio > 2.5 and v >= 1.8 * max(med, 1)
        if anomalo:
            atual.append((d, v))
            continue
        if atual:
            episodios.append({
                "inicio": atual[0][0].isoformat(),
                "fim": atual[-1][0].isoformat(),
                "dias": len(atual),
                "postagens": sum(v2 for _, v2 in atual),
                "maximo_dia": max(v2 for _, v2 in atual),
                "mediana_base": med,
                "z_robusto_max": round(max((v2 - med) / desvio for _, v2 in atual), 1),
            })
            atual = []
    return episodios


def detectar_silencios(serie):
    """Sequências de dias zerados que seriam improváveis pelo comportamento-base.

    p0 = chance de um dia qualquer ser zerado (suavização de Laplace).
    Um silêncio de k dias tem chance ~ p0^k; abaixo de 1% vira anomalia.
    """
    if len(serie) < 7:
        return []
    zerados = sum(1 for _, v in serie if v == 0)
    p0 = (zerados + 1) / (len(serie) + 2)
    silencios, atual = [], []
    for d, v in serie + [(None, 1)]:  # sentinela fecha a última sequência
        if v == 0 and d is not None:
            atual.append(d)
            continue
        if atual:
            k = len(atual)
            chance = p0 ** k
            if chance < 0.01:
                antes = [v2 for d2, v2 in serie if d2 < atual[0]][-7:]
                depois = [v2 for d2, v2 in serie if d2 > atual[-1]][:7]
                silencios.append({
                    "dia_zero": atual[0].isoformat(),
                    "ultimo_dia_mudo": atual[-1].isoformat(),
                    "dias": k,
                    "chance_ao_acaso": f"{chance:.2e}",
                    "media_7d_antes": round(statistics.mean(antes), 1) if antes else None,
                    "media_7d_depois": round(statistics.mean(depois), 1) if depois else None,
                })
            atual = []
    return silencios


def indicio_automacao(horarios):
    """Bot tem relógio: muitos posts no mesmo minuto da hora e intervalos regulares."""
    if len(horarios) < 20:
        return None
    minutos = Counter(dt.minute for dt in horarios)
    minuto, qtd = minutos.most_common(1)[0]
    fracao = qtd / len(horarios)
    intervalos = [(b - a).total_seconds() for a, b in zip(horarios, horarios[1:]) if b > a]
    cv = statistics.pstdev(intervalos) / statistics.mean(intervalos) if intervalos else 0
    suspeito = fracao > 0.4 or cv < 0.15
    return {
        "minuto_mais_comum": minuto,
        "fracao_no_mesmo_minuto": round(fracao, 3),
        "coef_variacao_intervalos": round(cv, 3),
        "suspeito": suspeito,
        "confianca": "M" if suspeito and fracao > 0.6 else "B",
    }


def analisar(horarios, fuso=None):
    if not horarios:
        raise SystemExit("Nenhum horário válido no arquivo.")
    inferido = inferir_fuso(horarios)
    deslocamento = parse_fuso(fuso) if fuso else timedelta(hours=inferido["deslocamento_horas"])
    serie = serie_diaria(horarios, deslocamento)
    grade = heatmap(horarios, deslocamento)
    picos = detectar_picos(serie)
    silencios = detectar_silencios(serie)
    bot = indicio_automacao(horarios)

    achados = []
    achados.append({
        "titulo": f"Fuso provável {inferido['fuso']}",
        "confianca": inferido["confianca"],
        "evidencia": f"janela mais quieta {inferido['janela_quieta_utc']} UTC "
                     f"(contraste {inferido['contraste']}: 0 = sono nítido, 1 = sem padrão)",
        "derrubaria": "trabalho noturno, viagem, postagem agendada ou conta compartilhada",
    })
    pico_hora = max(range(24), key=lambda h: sum(grade[d][h] for d in range(7)))
    achados.append({
        "titulo": f"Horário de maior atividade: {pico_hora:02d}h (hora local)",
        "confianca": "A" if len(horarios) >= 200 else "M",
        "evidencia": f"{sum(grade[d][pico_hora] for d in range(7))} de {len(horarios)} postagens",
        "derrubaria": "amostra concentrada num período atípico (férias, evento)",
    })
    for p in picos:
        periodo = p["inicio"] if p["dias"] == 1 else f"{p['inicio']} a {p['fim']}"
        achados.append({
            "titulo": f"Pico anômalo ({p['dias']} dia{'s' if p['dias'] > 1 else ''}): {periodo}",
            "confianca": "M" if p["dias"] >= 2 else "B",
            "evidencia": f"até {p['maximo_dia']} postagens/dia contra mediana {p['mediana_base']}; "
                         f"z robusto máx. {p['z_robusto_max']}",
            "derrubaria": "evento público que explica o volume (jogo, notícia, live)",
        })
    for s in silencios:
        achados.append({
            "titulo": f"Silêncio de {s['dias']} dias a partir de {s['dia_zero']} (dia zero)",
            "confianca": "M" if s["dias"] >= 5 else "B",
            "evidencia": f"chance ao acaso {s['chance_ao_acaso']}; média 7d antes "
                         f"{s['media_7d_antes']} → depois {s['media_7d_depois']}",
            "derrubaria": "postagens apagadas depois, coleta incompleta, conta suspensa pela plataforma",
        })
    if bot and bot["suspeito"]:
        achados.append({
            "titulo": "Padrão de relógio — possível automação",
            "confianca": bot["confianca"],
            "evidencia": f"{bot['fracao_no_mesmo_minuto']:.0%} no minuto :{bot['minuto_mais_comum']:02d}; "
                         f"coeficiente de variação {bot['coef_variacao_intervalos']}",
            "derrubaria": "agendador legítimo usado por pessoa real (social media)",
        })

    return {
        "ferramenta": f"RELÓGIO {VERSAO}",
        "postagens": len(horarios),
        "periodo": [horarios[0].isoformat(), horarios[-1].isoformat()],
        "fuso_usado": fuso or inferido["fuso"].replace("UTC", ""),
        "fuso_inferido": inferido,
        "heatmap": grade,
        "serie_diaria": [(d.isoformat(), v) for d, v in serie],
        "picos": picos,
        "silencios": silencios,
        "automacao": bot,
        "achados": achados,
    }


# ------------------------------------------------------------------ saída: terminal

BLOCOS = " ░▒▓█"


def imprimir(resultado, avisos, cor=True):
    def c(rgb, texto):
        return f"\033[38;2;{rgb}m{texto}\033[0m" if cor else texto
    menta, ambar, apagado = "94;230;196", "230;184;94", "138;150;147"
    print(c(menta, f"\n◆ RELÓGIO — {resultado['postagens']} postagens · fuso usado {resultado['fuso_usado']}"))
    print(c(apagado, f"  período {resultado['periodo'][0][:10]} → {resultado['periodo'][1][:10]}\n"))
    grade = resultado["heatmap"]
    maximo = max(max(l) for l in grade) or 1
    print(c(apagado, "       " + "".join(f"{h:02d}h   " for h in range(0, 24, 3))))
    for d, linha in enumerate(grade):
        celulas = "".join(BLOCOS[min(4, math.ceil(4 * v / maximo))] * 2 for v in linha)
        print(f"  {DIAS[d]}  " + c(menta, celulas))
    print(c(apagado, "       (cada par de caracteres = 1 hora; mais cheio = mais atividade)\n"))
    print("  ACHADOS")
    for a in resultado["achados"]:
        rotulo = {"A": c(menta, "[A]"), "M": c(ambar, "[M]"), "B": c(apagado, "[B]")}[a["confianca"]]
        print(f"  {rotulo} {a['titulo']}")
        print(c(apagado, f"      evidência: {a['evidencia']}"))
        print(c(apagado, f"      o que derrubaria: {a['derrubaria']}"))
    for av in avisos:
        print(c(ambar, f"  aviso: {av}"))
    print(c(apagado, "\n  Perfil é hipótese, não sentença. Combine com outras fontes antes de atribuir.\n"))


# ------------------------------------------------------------------ saída: HTML

def gerar_html(resultado, origem, sha):
    grade = resultado["heatmap"]
    maximo = max(max(l) for l in grade) or 1
    cel, esq, topo = 22, 46, 26
    rects = []
    for d in range(7):
        rects.append(f'<text x="{esq - 10}" y="{topo + d * cel + 15}" class="r" text-anchor="end">{DIAS[d]}</text>')
        for h in range(24):
            v = grade[d][h]
            op = 0.06 if v == 0 else 0.25 + 0.75 * v / maximo
            rects.append(f'<rect x="{esq + h * cel}" y="{topo + d * cel}" width="{cel - 3}" height="{cel - 3}" '
                         f'rx="3" fill="#5EE6C4" fill-opacity="{op:.2f}"><title>{DIAS[d]} {h:02d}h: {v}</title></rect>')
    for h in range(0, 24, 3):
        rects.append(f'<text x="{esq + h * cel}" y="{topo - 8}" class="r">{h:02d}h</text>')
    larg_hm = esq + 24 * cel + 10
    alt_hm = topo + 7 * cel + 10

    serie = resultado["serie_diaria"]
    dias_pico = set()
    for p in resultado["picos"]:
        d0, d1 = date.fromisoformat(p["inicio"]), date.fromisoformat(p["fim"])
        while d0 <= d1:
            dias_pico.add(d0.isoformat())
            d0 += timedelta(days=1)
    dias_mudos = set()
    for s in resultado["silencios"]:
        d0, d1 = date.fromisoformat(s["dia_zero"]), date.fromisoformat(s["ultimo_dia_mudo"])
        while d0 <= d1:
            dias_mudos.add(d0.isoformat())
            d0 += timedelta(days=1)
    vmax = max((v for _, v in serie), default=1) or 1
    larg_b = max(14, min(26, 900 // max(1, len(serie))))
    barras = []
    for i, (d, v) in enumerate(serie):
        altura = 140 * v / vmax
        cor = "#E6B85E" if d in dias_pico else "#2E7563"
        barras.append(f'<rect x="{i * larg_b}" y="{150 - altura:.1f}" width="{larg_b - 3}" height="{altura:.1f}" '
                      f'fill="{cor}" rx="2"><title>{d}: {v}</title></rect>')
        if d in dias_mudos:
            barras.append(f'<rect x="{i * larg_b}" y="146" width="{larg_b - 3}" height="4" fill="#E57A6B"/>')
    larg_serie = len(serie) * larg_b

    linhas = []
    for a in resultado["achados"]:
        classe = {"A": "a", "M": "m", "B": "b"}[a["confianca"]]
        linhas.append(
            f'<tr><td><span class="selo {classe}">{a["confianca"]}</span></td>'
            f'<td><b>{html.escape(a["titulo"])}</b><br><small>{html.escape(a["evidencia"])}</small></td>'
            f'<td><small>{html.escape(a["derrubaria"])}</small></td></tr>')

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RELÓGIO · relatório</title>
<style>
:root{{--fundo:#0B0F10;--sup:#10181A;--borda:#1F2B29;--txt:#DCE4E2;--apag:#8A9693;--menta:#5EE6C4;--ambar:#E6B85E;--coral:#E57A6B}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fundo);color:var(--txt);font:15px/1.55 Inter,system-ui,sans-serif}}
main{{max-width:1040px;margin:0 auto;padding:32px 16px 64px}}
.rot{{font:11px/1 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.28em;text-transform:uppercase;color:var(--apag)}}
h1{{font-size:34px;margin:8px 0 4px;letter-spacing:-.02em}}h1 em{{color:var(--menta);font-style:normal}}
.card{{background:var(--sup);border:1px solid var(--borda);border-radius:12px;padding:20px;margin:18px 0;overflow-x:auto}}
svg .r{{font:11px "JetBrains Mono",monospace;fill:var(--apag)}}
table{{width:100%;border-collapse:collapse}}td{{padding:10px 8px;border-top:1px solid var(--borda);vertical-align:top}}
small{{color:var(--apag)}}.selo{{display:inline-block;width:26px;text-align:center;border-radius:6px;font:700 12px/22px monospace}}
.a{{background:rgba(94,230,196,.15);color:var(--menta)}}.m{{background:rgba(230,184,94,.15);color:var(--ambar)}}.b{{background:#1a2224;color:var(--apag)}}
.leg span{{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 6px 0 14px;vertical-align:middle}}
footer{{color:var(--apag);font-size:13px;border-top:1px solid var(--borda);margin-top:28px;padding-top:16px}}
code{{font-family:"JetBrains Mono",monospace;font-size:12px;word-break:break-all}}
</style></head><body><main>
<div class="rot">DEIVOSINT · TOCAIA · fase T — traçar</div>
<h1>O relógio do alvo <em>é um mapa.</em></h1>
<div class="rot">{resultado['postagens']} postagens · {resultado['periodo'][0][:10]} → {resultado['periodo'][1][:10]} · fuso usado {html.escape(resultado['fuso_usado'])}</div>
<div class="card"><div class="rot">padrão de vida · hora × dia (hora local)</div>
<svg viewBox="0 0 {larg_hm} {alt_hm}" width="{larg_hm}" height="{alt_hm}" role="img" aria-label="Heatmap de atividade por hora e dia">{''.join(rects)}</svg></div>
<div class="card"><div class="rot">atividade diária</div>
<svg viewBox="0 0 {larg_serie} 152" width="{larg_serie}" height="152" role="img" aria-label="Postagens por dia">{''.join(barras)}</svg>
<div class="leg rot"><span style="background:#2E7563"></span>linha de base<span style="background:#E6B85E"></span>pico anômalo<span style="background:#E57A6B"></span>silêncio · o gap</div></div>
<div class="card"><div class="rot">achados · confiança A/M/B · o que derrubaria a hipótese</div>
<table>{''.join(linhas)}</table></div>
<footer>Cadeia de custódia — arquivo de origem <code>{html.escape(str(origem))}</code><br>
SHA-256 <code>{sha}</code><br>
Gerado por RELÓGIO {VERSAO} em {datetime.now(timezone.utc).replace(microsecond=0).isoformat()} (UTC).
Rode <code>trem manifesto --saida manifesto.json</code> e anexe ao relatório.<br><br>
Perfil é hipótese, não sentença. Fonte pública, zero interação, base legal (LGPD · Marco Civil).</footer>
</main></body></html>
"""


# ------------------------------------------------------------------ entrada

def caso_demo():
    """Procura o CSV do caso #BX-7 (no repositório ou no sistema instalado)."""
    candidatos = [Path(__file__).resolve().parents[2] / "casos" / "demo-bx7" / "postagens.csv",
                  Path("/opt/tocaia/casos/demo-bx7/postagens.csv")]
    for c in candidatos:
        try:
            if c.exists():
                return c
        except OSError:
            continue
    raise SystemExit("Caso demo não encontrado. Passe o caminho do CSV.")


def main(argv=None):
    p = argparse.ArgumentParser(prog="relogio", description="RELÓGIO — o relógio do alvo é um mapa.")
    p.add_argument("csv", nargs="?", help="CSV com uma coluna de data/hora (ISO 8601 ou epoch)")
    p.add_argument("--fuso", help="fuso para exibir, ex.: -03:00 (padrão: o inferido)")
    p.add_argument("--html", help="salva relatório HTML neste caminho")
    p.add_argument("--json", help="salva os achados em JSON neste caminho")
    p.add_argument("--demo", action="store_true", help="usa o caso sintético #BX-7")
    p.add_argument("--sem-cor", action="store_true")
    p.add_argument("--version", action="version", version=f"RELÓGIO {VERSAO}")
    a = p.parse_args(argv)

    origem = caso_demo() if a.demo or not a.csv else Path(a.csv)
    if not a.csv and not a.demo:
        print("(sem arquivo: rodando o caso sintético #BX-7 — use --help para ver as opções)")
    horarios, avisos = ler_horarios(origem)
    resultado = analisar(horarios, a.fuso)
    sha = sha256_arquivo(origem)
    resultado["origem"] = {"arquivo": str(origem), "sha256": sha}
    imprimir(resultado, avisos, cor=sys.stdout.isatty() and not a.sem_cor)
    if a.html:
        Path(a.html).write_text(gerar_html(resultado, origem, sha), encoding="utf-8")
        print(f"✓ relatório HTML: {a.html}")
    if a.json:
        Path(a.json).write_text(json.dumps(resultado, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"✓ achados em JSON: {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

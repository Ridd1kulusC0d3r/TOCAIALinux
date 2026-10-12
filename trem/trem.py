#!/usr/bin/env python3
"""trem — lançador da TOCAIA OSINT Linux. Só biblioteca padrão.

Uso:
    trem                 lista as tools agrupadas pelas fases da TOCAIA
    trem fases           mostra as fases e o que cada uma faz
    trem <tool> [args]   roda a tool (instala sob demanda, se preciso)
    trem versao          versão da distro e do catálogo

Em Minas tudo é trem. Aqui também.
"""
import json
import os
import subprocess
import sys
import venv
from pathlib import Path

VERSAO = "1.0.0"
CODINOME = "Tropeiro"

FASES = {
    "Traçar": "definir pergunta, escopo e limites éticos",
    "Observar": "coletar com OPSEC, sem tocar no alvo",
    "Cercar": "pivotar identificadores (username, e-mail, domínio)",
    "Aguardar": "monitorar no tempo; a ausência também é sinal",
    "Interpretar": "correlacionar, pesar confiança, montar grafo",
    "Atribuir": "concluir com cadeia de custódia e relatório",
}


def achar_base():
    """Onde mora o catálogo: $TREM_HOME, a pasta do repo ou /opt/tocaia."""
    if os.environ.get("TREM_HOME"):
        return Path(os.environ["TREM_HOME"])
    aqui = Path(__file__).resolve().parent.parent
    if (aqui / "catalogo.json").exists():
        return aqui
    return Path("/opt/tocaia")


BASE = achar_base()


def carregar_catalogo():
    arquivo = BASE / "catalogo.json"
    if not arquivo.exists():
        sys.exit(f"uai, sô: não achei o catálogo em {arquivo}")
    return json.loads(arquivo.read_text(encoding="utf-8"))


def pasta_venv(nome):
    return BASE / "venvs" / nome


def status(nome, t):
    if t["tipo"] == "pyz":
        return "pronta" if (BASE / "dist" / t["arquivo"]).exists() else "falta build"
    if t["tipo"] == "pip":
        return "pronta" if pasta_venv(nome).exists() else "sob demanda"
    return "planejada"


def listar(cat):
    prontas = sum(1 for n, t in cat.items() if status(n, t) == "pronta")
    print(f"uai, sô — TOCAIA {VERSAO} \"{CODINOME}\": {prontas} trens prontos, "
          f"{len(cat) - prontas} sob demanda ou planejados\n")
    for fase in FASES:
        do_grupo = {n: t for n, t in cat.items() if t["fase"] == fase}
        if not do_grupo:
            continue
        print(f"[{fase.upper()}] {FASES[fase]}")
        for nome, t in do_grupo.items():
            print(f"  {nome:12} {status(nome, t):12} {t['desc']}")
        print()


def mostrar_fases():
    for i, (fase, desc) in enumerate(FASES.items(), 1):
        print(f"{i}. {fase:12} {desc}")


def instalar(nome, t):
    destino = pasta_venv(nome)
    print(f"instalando {nome} em {destino} (só na primeira vez)...")
    venv.create(destino, with_pip=True)
    pip = destino / ("Scripts" if os.name == "nt" else "bin") / "pip"
    subprocess.run([str(pip), "install", "--quiet", t["pip"]], check=True)


def comando_de(nome, t):
    if t["tipo"] == "pyz":
        arquivo = BASE / "dist" / t["arquivo"]
        if not arquivo.exists():
            sys.exit(f"{nome}: rode antes `python3 build.py` para empacotar as tools")
        return [sys.executable, str(arquivo)]
    if t["tipo"] == "pip":
        if not pasta_venv(nome).exists():
            instalar(nome, t)
        pasta = "Scripts" if os.name == "nt" else "bin"
        return [str(pasta_venv(nome) / pasta / t["comando"])]
    sys.exit(f"{nome}: ainda está planejada ({t.get('origem', 'sem origem')}). "
             "Empacote em tools/ e mude o tipo para pyz.")


def main(argv):
    cat = carregar_catalogo()
    if not argv or argv[0] in ("lista", "-l"):
        listar(cat)
        return 0
    if argv[0] == "fases":
        mostrar_fases()
        return 0
    if argv[0] in ("versao", "--versao", "-V"):
        print(f"TOCAIA OSINT Linux {VERSAO} \"{CODINOME}\" — catálogo com {len(cat)} trens")
        return 0
    if argv[0] in ("ajuda", "-h", "--help"):
        print(__doc__)
        return 0
    nome = argv[0]
    if nome not in cat:
        print(f"não conheço o trem '{nome}'. Rode `trem` para ver a lista.")
        return 2
    ambiente = dict(os.environ, TREM_HOME=str(BASE))
    return subprocess.call([*comando_de(nome, cat[nome]), *argv[1:]], env=ambiente)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

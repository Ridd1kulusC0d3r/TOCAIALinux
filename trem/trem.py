#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trem — o lançador da TOCAIA OSINT Linux.

Em Minas, tudo é "trem". Aqui, cada ferramenta também é:
    trem                    lista o catálogo, agrupado pelas fases da TOCAIA
    trem fases              mostra as seis fases da doutrina
    trem <nome> [args...]   roda uma ferramenta (instala sob demanda se precisar)
    trem info <nome>        detalhes de uma ferramenta
    trem instalar <nome>    instala uma ferramenta sob demanda sem rodar
    trem manifesto          gera o manifesto de cadeia de custódia do ferramental
    trem manifesto --verificar arquivo.json
    trem menu --destino DIR gera os atalhos do menu gráfico (.desktop)
    trem doutor             checagem de saúde do ambiente
    trem etica              regras de engajamento (leia antes de investigar)
    trem saudacao           a mensagem do terminal ("uai, sô")
    trem versao

Regras de projeto:
  * só biblioteca padrão do Python (stdlib) — roda em Debian, Alpine, WSL e Colab;
  * nenhuma ferramenta de terceiro vem pré-instalada: tudo que é "pip" entra num
    ambiente virtual próprio, criado na primeira vez que você usa;
  * o catálogo (catalogo.json) é a única fonte da verdade: menu, lista, manifesto
    e documentação leem dele.
"""

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from datetime import datetime, timezone
from pathlib import Path

VERSAO = "1.0.0"
CODINOME = "Tropeiro"

# --------------------------------------------------------------------------
# Onde as coisas moram
# --------------------------------------------------------------------------


def _descobrir_home():
    """Pasta-base da TOCAIA.

    Ordem: variável TOCAIA_HOME > /opt/tocaia (sistema instalado) > raiz do
    repositório (quando você roda direto do git clone, para estudar).
    """
    if os.environ.get("TOCAIA_HOME"):
        return Path(os.environ["TOCAIA_HOME"])
    if Path("/opt/tocaia/catalogo.json").exists():
        return Path("/opt/tocaia")
    return Path(__file__).resolve().parent.parent  # .../repo/trem/trem.py -> .../repo


HOME = _descobrir_home()
DADOS = Path(os.environ.get("TOCAIA_DADOS", Path.home() / ".local" / "share" / "tocaia"))


def caminho_catalogo():
    for c in (HOME / "catalogo.json", HOME / "catalogo" / "catalogo.json"):
        if c.exists():
            return c
    raise SystemExit(f"uai: não achei o catalogo.json em {HOME}")


def edicao():
    """debian | alpine | nuvem | dev — usada no manifesto e em avisos."""
    if os.environ.get("TOCAIA_EDICAO"):
        return os.environ["TOCAIA_EDICAO"]
    rel = Path("/etc/tocaia-release")
    if rel.exists():
        for linha in rel.read_text(encoding="utf-8").splitlines():
            if linha.startswith("EDICAO="):
                return linha.split("=", 1)[1].strip().strip('"')
    return "dev"


# --------------------------------------------------------------------------
# Cores (só se a saída for um terminal de verdade)
# --------------------------------------------------------------------------

_COR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _COR else ""


MENTA = _rgb(94, 230, 196)
MENTA_ESC = _rgb(65, 154, 133)
AMBAR = _rgb(230, 184, 94)
CORAL = _rgb(229, 122, 107)
APAGADO = _rgb(138, 150, 147)
NEGRITO = "\033[1m" if _COR else ""
FIM = "\033[0m" if _COR else ""


# --------------------------------------------------------------------------
# Catálogo
# --------------------------------------------------------------------------

TIPOS = {"pyz", "pip", "git", "sistema", "web", "interno"}
STATUS = {"pronta", "planejada"}


def carregar_catalogo():
    dados = json.loads(caminho_catalogo().read_text(encoding="utf-8"))
    validar_catalogo(dados)
    return dados


def validar_catalogo(dados):
    """Confere o catálogo e devolve a lista de problemas (vazia = tudo certo).

    Levanta ValueError se houver problema — o build da ISO e o CI usam isso
    para não publicar um catálogo quebrado.
    """
    problemas = []
    fases = dados.get("fases", {})
    for nome, t in dados.get("ferramentas", {}).items():
        def falta(campo):
            if not t.get(campo):
                problemas.append(f"{nome}: falta o campo '{campo}'")
        for campo in ("fase", "tipo", "desc", "status", "origem"):
            falta(campo)
        if t.get("fase") not in fases:
            problemas.append(f"{nome}: fase '{t.get('fase')}' não existe")
        if t.get("tipo") not in TIPOS:
            problemas.append(f"{nome}: tipo '{t.get('tipo')}' inválido")
        if t.get("status") not in STATUS:
            problemas.append(f"{nome}: status '{t.get('status')}' inválido")
        if t.get("status") == "pronta":
            exigidos = {"pyz": ["arquivo"], "pip": ["pip", "comando"], "git": ["repo", "entrada"],
                        "sistema": ["comando"], "web": ["url"], "interno": ["comando"]}
            for campo in exigidos.get(t.get("tipo"), []):
                falta(campo)
        if nome != nome.lower() or " " in nome:
            problemas.append(f"{nome}: nome deve ser minúsculo e sem espaço")
    if problemas:
        raise ValueError("catálogo inválido:\n  - " + "\n  - ".join(problemas))
    return problemas


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------


def _venv_dir(nome):
    return DADOS / "venvs" / nome


def _bin_do_venv(nome, comando):
    pasta = "Scripts" if os.name == "nt" else "bin"
    return _venv_dir(nome) / pasta / comando


def instalada(nome, t):
    tipo = t["tipo"]
    if t["status"] != "pronta":
        return False
    if tipo == "pyz":
        return _local_pyz(t) is not None
    if tipo == "pip":
        return _bin_do_venv(nome, t["comando"]).exists()
    if tipo == "git":
        return (DADOS / "git" / nome / t["entrada"]).exists()
    if tipo == "sistema":
        return shutil.which(t["comando"]) is not None
    return True  # web e interno não precisam instalar


def _local_pyz(t):
    """Procura o .pyz instalado; no repositório, aceita a pasta-fonte."""
    candidatos = [HOME / "ferramentas" / t["arquivo"]]
    if t.get("fonte"):
        candidatos.append(HOME / "ferramentas" / t["fonte"])  # pasta com __main__.py
    for c in candidatos:
        if c.exists():
            return c
    return None


def instalar(nome, t):
    """Instala sob demanda. Só pip e git precisam disso."""
    tipo = t["tipo"]
    if tipo == "pip":
        destino = _venv_dir(nome)
        print(f"{APAGADO}» criando ambiente isolado em {destino}{FIM}")
        destino.parent.mkdir(parents=True, exist_ok=True)
        python_venv = destino / ("Scripts" if os.name == "nt" else "bin") / "python"
        try:
            venv.create(destino, with_pip=True, clear=True)
            pip = [str(python_venv), "-m", "pip"]
        except Exception:
            # Alpine e alguns contêineres não trazem ensurepip: usamos o pip do
            # sistema apontando para o venv (pip >= 22.3 aceita --python).
            venv.create(destino, with_pip=False, clear=True)
            pip = [sys.executable, "-m", "pip", "--python", str(python_venv)]
        subprocess.run([*pip, "install", "--disable-pip-version-check", "-q", t["pip"]], check=True)
    elif tipo == "git":
        destino = DADOS / "git" / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            subprocess.run(["git", "clone", "--depth", "1", t["repo"], str(destino)], check=True)
    elif tipo == "sistema":
        dica = {"debian": t.get("apt"), "alpine": t.get("apk")}.get(edicao())
        raise SystemExit(f"{AMBAR}'{t['comando']}' não está instalado.{FIM}"
                         + (f" Instale com: sudo apt install {dica}" if edicao() == "debian" and dica else "")
                         + (f" Instale com: apk add {dica}" if edicao() == "alpine" and dica else ""))
    print(f"{MENTA}✓ {nome} pronta{FIM}")


def montar_comando(nome, t, args):
    tipo = t["tipo"]
    if tipo == "pyz":
        local = _local_pyz(t)
        if local is None:
            raise SystemExit(f"uai: {t['arquivo']} não encontrado em {HOME / 'ferramentas'}")
        return [sys.executable, str(local), *args]
    if tipo == "pip":
        return [str(_bin_do_venv(nome, t["comando"])), *args]
    if tipo == "git":
        return [sys.executable, str(DADOS / "git" / nome / t["entrada"]), *args]
    if tipo == "sistema":
        return [t["comando"], *args]
    raise ValueError(tipo)


def rodar(nome, args):
    cat = carregar_catalogo()
    t = cat["ferramentas"].get(nome)
    if t is None:
        sugestoes = [n for n in cat["ferramentas"] if n.startswith(nome[:2])]
        dica = f" Quis dizer: {', '.join(sugestoes)}?" if sugestoes else ""
        raise SystemExit(f"uai, não conheço esse trem: '{nome}'.{dica} Veja `trem lista`.")
    if t["status"] != "pronta":
        raise SystemExit(f"{AMBAR}{nome} ainda está no forno (status: planejada).{FIM} "
                         f"Veja docs/PROJETOS.md para o plano de integração.")
    garantir_etica()
    if t["tipo"] == "web":
        print(f"{MENTA}{t['url']}{FIM}")
        abrir = shutil.which("xdg-open")
        if abrir and os.environ.get("DISPLAY"):
            subprocess.Popen([abrir, t["url"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 0
    if t["tipo"] == "interno":
        return main([t["comando"], *args])
    if not instalada(nome, t):
        instalar(nome, t)
    return subprocess.call(montar_comando(nome, t, args))


# --------------------------------------------------------------------------
# Ética: as regras de engajamento do slide 3, na primeira vez
# --------------------------------------------------------------------------

REGRAS = """\
  $ regras_de_engajamento --check
  fonte .................. pública · sem burlar barreira
  interação com o alvo ... zero
  base legal ............. LGPD · Marco Civil
  finalidade ............. legítima & proporcional

  $ se cruzar_a_linha
  curtir · seguir · contatar ... destrói a tocaia
  enganar · invadir ............ vira crime

  Perfil é hipótese, não sentença. Rotule a confiança (A/M/B).
  Ler não é invadir. Esperar não é emboscar.
"""


def mostrar_etica():
    print(f"\n{NEGRITO}TOCAIA · regras de engajamento{FIM}\n")
    for linha in REGRAS.splitlines():
        cor = CORAL if "crime" in linha or "destrói" in linha else (MENTA if "$" in linha else "")
        print(f"{cor}{linha}{FIM}")
    print()


def garantir_etica():
    """Mostra as regras uma única vez por usuário (ou TOCAIA_ETICA=aceito)."""
    marca = DADOS / "etica-aceita"
    if marca.exists() or os.environ.get("TOCAIA_ETICA") == "aceito":
        return
    mostrar_etica()
    if sys.stdin.isatty():
        resposta = input("Digite 'li' para confirmar que leu e concorda: ").strip().lower()
        if resposta != "li":
            raise SystemExit("Sem problema. Quando quiser, rode `trem etica`.")
    DADOS.mkdir(parents=True, exist_ok=True)
    marca.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")


# --------------------------------------------------------------------------
# Listagens
# --------------------------------------------------------------------------


def listar(fase_filtro=None):
    cat = carregar_catalogo()
    por_fase = {f: [] for f in cat["fases"]}
    for nome, t in cat["ferramentas"].items():
        por_fase[t["fase"]].append((nome, t))
    for fase, itens in por_fase.items():
        if fase_filtro and fase != fase_filtro:
            continue
        info = cat["fases"][fase]
        print(f"\n{MENTA}{NEGRITO}{info['letra']}  {info['nome'].upper()}{FIM}  {APAGADO}{info['lema']}{FIM}")
        for nome, t in sorted(itens):
            if t["status"] != "pronta":
                selo = f"{APAGADO}no forno   {FIM}"
            elif instalada(nome, t):
                selo = f"{MENTA}pronta     {FIM}"
            else:
                selo = f"{AMBAR}sob demanda{FIM}"
            dono = "◆" if t["origem"] == "propria" else " "
            print(f"   {MENTA_ESC}{dono}{FIM} {nome:<12} {selo} {t['desc']}")
    print(f"\n{APAGADO}◆ = ferramenta DEIVOSINT · `trem info <nome>` para detalhes{FIM}\n")


def mostrar_fases():
    cat = carregar_catalogo()
    print(f"\n{NEGRITO}TOCAIA não é um nome. É um método.{FIM}\n")
    for fase, info in cat["fases"].items():
        print(f"  {MENTA}{NEGRITO}{info['letra']}{FIM}  {info['nome']:<12} {info['lema']}")
        print(f"     {APAGADO}{info['explica']}{FIM}")
    print()


def mostrar_info(nome):
    cat = carregar_catalogo()
    t = cat["ferramentas"].get(nome)
    if not t:
        raise SystemExit(f"uai, não conheço '{nome}'.")
    fase = cat["fases"][t["fase"]]
    print(f"\n{NEGRITO}{nome}{FIM} — {t['desc']}")
    print(f"  fase ....... {fase['letra']} · {fase['nome']}")
    for campo in ("tipo", "status", "origem", "autor", "licenca", "pip", "repo", "url", "apt", "apk"):
        if t.get(campo):
            print(f"  {campo:<10} {t[campo]}")
    if t.get("uso"):
        print(f"  exemplo .... {MENTA}{t['uso']}{FIM}")
    if t.get("nota"):
        print(f"  nota ....... {t['nota']}")
    print()


# --------------------------------------------------------------------------
# Menu gráfico: um .desktop por ferramenta, categoria = fase
# --------------------------------------------------------------------------


def gerar_menu(destino):
    cat = carregar_catalogo()
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    feitos = 0
    for nome, t in cat["ferramentas"].items():
        if t["status"] != "pronta":
            continue
        fase = cat["fases"][t["fase"]]
        categoria = "X-TOCAIA-" + fase["nome"].replace("ç", "c").replace("Ç", "C")
        comando = f"trem {nome}"
        if t["tipo"] == "web":
            linha_exec = f"Exec={comando}\nTerminal=false\n"
        else:
            # abre um terminal com a ficha da ferramenta e deixa o shell pronto
            linha_exec = (f"Exec=xfce4-terminal --title='TOCAIA · {nome}' "
                          f"-x bash -lc 'trem info {nome}; exec bash'\nTerminal=false\n")
        (destino / f"tocaia-{nome}.desktop").write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={nome.upper()}\n"
            f"Comment={t['desc']}\n"
            f"{linha_exec}"
            f"Icon=tocaia-{t['fase']}\n"
            f"Categories={categoria};\n",
            encoding="utf-8",
        )
        feitos += 1
    print(f"{MENTA}✓ {feitos} atalhos gerados em {destino}{FIM}")
    return feitos


# --------------------------------------------------------------------------
# Manifesto: cadeia de custódia do ferramental
# --------------------------------------------------------------------------


def _sha256(caminho):
    h = hashlib.sha256()
    caminho = Path(caminho)
    arquivos = [caminho] if caminho.is_file() else sorted(p for p in caminho.rglob("*") if p.is_file())
    for arq in arquivos:
        if caminho.is_dir():
            h.update(str(arq.relative_to(caminho)).encode())
        h.update(arq.read_bytes())
    return h.hexdigest()


def _versao_pip(nome):
    """Lê a versão instalada no venv sem importar nada de lá."""
    for sp in _venv_dir(nome).glob("lib/python*/site-packages"):
        for meta in sp.glob("*.dist-info/METADATA"):
            texto = meta.read_text(encoding="utf-8", errors="replace").splitlines()
            campos = dict(l.split(": ", 1) for l in texto[:10] if ": " in l)
            return f"{campos.get('Name')}=={campos.get('Version')}" if campos.get("Version") else None
    return None


def _corpo_manifesto():
    cat = carregar_catalogo()
    ferramentas = {}
    for nome, t in sorted(cat["ferramentas"].items()):
        if t["status"] != "pronta":
            continue
        item = {"tipo": t["tipo"], "fase": t["fase"], "instalada": instalada(nome, t)}
        if t["tipo"] == "pyz" and _local_pyz(t):
            item["sha256"] = _sha256(_local_pyz(t))
        elif t["tipo"] == "pip" and item["instalada"]:
            item["versao"] = _versao_pip(nome)
        elif t["tipo"] == "sistema" and item["instalada"]:
            item["caminho"] = shutil.which(t["comando"])
        ferramentas[nome] = item
    return {
        "tocaia": {"versao": VERSAO, "codinome": CODINOME, "edicao": edicao()},
        "ambiente": {
            "sistema": platform.system(),
            "plataforma": platform.platform(),
            "python": platform.python_version(),
            "maquina": platform.machine(),
        },
        "catalogo_sha256": _sha256(caminho_catalogo()),
        "trem_sha256": _sha256(Path(__file__)),
        "ferramentas": ferramentas,
    }


def manifesto(saida=None):
    corpo = _corpo_manifesto()
    gerado = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    # O ID é o hash do corpo canônico: qualquer mudança no ferramental muda o ID.
    canonico = json.dumps(corpo, sort_keys=True, ensure_ascii=False).encode("utf-8")
    doc = {"id": hashlib.sha256(canonico).hexdigest()[:16], "gerado_em_utc": gerado, **corpo}
    texto = json.dumps(doc, indent=2, ensure_ascii=False)
    if saida:
        Path(saida).write_text(texto + "\n", encoding="utf-8")
        print(f"{MENTA}✓ manifesto {doc['id']} salvo em {saida}{FIM}")
        print(f"{APAGADO}  Cite esse ID no relatório: 'coleta feita com o ferramental TOCAIA {doc['id']}'.{FIM}")
    else:
        print(texto)
    return doc


def verificar_manifesto(arquivo):
    doc = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    corpo = {k: v for k, v in doc.items() if k not in ("id", "gerado_em_utc")}
    canonico = json.dumps(corpo, sort_keys=True, ensure_ascii=False).encode("utf-8")
    integro = hashlib.sha256(canonico).hexdigest()[:16] == doc["id"]
    atual = _corpo_manifesto()
    mesmo_ambiente = atual["ferramentas"] == corpo["ferramentas"] and \
        atual["catalogo_sha256"] == corpo["catalogo_sha256"]
    print(f"  arquivo íntegro ............ {'sim' if integro else 'NÃO — foi alterado'}")
    print(f"  ferramental atual é o mesmo  {'sim' if mesmo_ambiente else 'não (versões ou catálogo mudaram)'}")
    return integro, mesmo_ambiente


# --------------------------------------------------------------------------
# Saúde e saudação
# --------------------------------------------------------------------------


def doutor():
    ok = True
    def linha(rotulo, passou, extra=""):
        nonlocal ok
        ok = ok and passou
        marca = f"{MENTA}✓{FIM}" if passou else f"{CORAL}✗{FIM}"
        print(f"  {marca} {rotulo:<28} {APAGADO}{extra}{FIM}")
    print(f"\n{NEGRITO}trem doutor{FIM} — edição {edicao()}, home {HOME}\n")
    linha("Python 3.9 ou mais novo", sys.version_info >= (3, 9), platform.python_version())
    try:
        cat = carregar_catalogo()
        linha("catálogo válido", True, f"{len(cat['ferramentas'])} ferramentas")
    except Exception as e:  # noqa: BLE001 — queremos mostrar qualquer falha
        linha("catálogo válido", False, str(e).splitlines()[0])
        cat = {"ferramentas": {}}
    linha("módulo venv disponível", True)
    linha("git disponível", shutil.which("git") is not None, "necessário para tools tipo git")
    for nome, t in cat["ferramentas"].items():
        if t.get("tipo") == "pyz" and t.get("status") == "pronta":
            linha(f"ferramenta {nome}", _local_pyz(t) is not None)
    DADOS.mkdir(parents=True, exist_ok=True)
    linha("pasta de dados gravável", os.access(DADOS, os.W_OK), str(DADOS))
    print()
    return 0 if ok else 1


def saudacao():
    try:
        cat = carregar_catalogo()
        prontas = sum(1 for n, t in cat["ferramentas"].items() if instalada(n, t))
        demanda = sum(1 for n, t in cat["ferramentas"].items()
                      if t["status"] == "pronta" and not instalada(n, t))
    except Exception:  # noqa: BLE001 — a saudação nunca pode quebrar o terminal
        prontas = demanda = 0
    print(f"{MENTA}◆ uai, sô{FIM} — TOCAIA OSINT Linux {VERSAO} \"{CODINOME}\" · "
          f"{prontas} trens prontos, {demanda} sob demanda")
    print(f"{APAGADO}  leia o padrão · ouça o silêncio · posicione-se e espere   (trem · trem fases · trem etica){FIM}")


# --------------------------------------------------------------------------
# Entrada
# --------------------------------------------------------------------------


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("lista", "ls"):
        fase = None
        if "--fase" in argv:
            fase = argv[argv.index("--fase") + 1]
        listar(fase)
        return 0
    cmd, resto = argv[0], argv[1:]
    if cmd in ("-h", "--help", "ajuda"):
        print(__doc__)
        return 0
    if cmd in ("versao", "--version", "-V"):
        print(f"trem {VERSAO} \"{CODINOME}\" (edição {edicao()})")
        return 0
    if cmd == "fases":
        mostrar_fases()
        return 0
    if cmd == "info":
        mostrar_info(resto[0] if resto else "")
        return 0
    if cmd == "instalar":
        cat = carregar_catalogo()
        nome = resto[0] if resto else ""
        if nome not in cat["ferramentas"]:
            raise SystemExit(f"uai, não conheço '{nome}'.")
        instalar(nome, cat["ferramentas"][nome])
        return 0
    if cmd == "menu":
        destino = resto[resto.index("--destino") + 1] if "--destino" in resto else "."
        gerar_menu(destino)
        return 0
    if cmd == "manifesto":
        if "--verificar" in resto:
            integro, _ = verificar_manifesto(resto[resto.index("--verificar") + 1])
            return 0 if integro else 2
        saida = resto[resto.index("--saida") + 1] if "--saida" in resto else None
        manifesto(saida)
        return 0
    if cmd == "doutor":
        return doutor()
    if cmd == "etica":
        mostrar_etica()
        return 0
    if cmd == "saudacao":
        saudacao()
        return 0
    if cmd == "validar":
        carregar_catalogo()
        print(f"{MENTA}✓ catálogo válido{FIM}")
        return 0
    return rodar(cmd, resto)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nfalou, até mais.")
        sys.exit(130)
    except BrokenPipeError:
        # saída canalizada para `head`, `less q`, etc. — encerra em silêncio
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)

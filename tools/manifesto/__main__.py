"""manifesto — cadeia de custódia do ferramental.

Gera um manifesto com o SHA-256 de cada tool empacotada, a versão de cada
tool instalada sob demanda e o ambiente (SO, Python). O ID do manifesto é o
hash do próprio conteúdo: cite esse ID no relatório da investigação.

No celular (edição "Matula"), entra também a ficha do APARELHO de coleta:
modelo, Android, patch de segurança e estado do bootloader/verified boot,
lidos do `dispositivo.json` que o tocaia_celular.py grava (ou do getprop).

    trem manifesto                  gera e imprime o manifesto
    trem manifesto -o man.json      grava em arquivo
    trem manifesto --verificar man.json   confere se o ambiente mudou
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def base():
    if os.environ.get("TREM_HOME"):
        return Path(os.environ["TREM_HOME"])
    return Path("/opt/tocaia")


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def versoes_pip(pasta_venv):
    pip = pasta_venv / ("Scripts" if os.name == "nt" else "bin") / "pip"
    if not pip.exists():
        return {}
    saida = subprocess.run([str(pip), "freeze"], capture_output=True, text=True).stdout
    return dict(linha.split("==", 1) for linha in saida.splitlines() if "==" in linha)


def dispositivo(raiz):
    """Ficha do aparelho Android, se houver. Fora do celular, devolve {}."""
    ficha = raiz / "dispositivo.json"
    if ficha.exists():
        dados = json.loads(ficha.read_text(encoding="utf-8"))
        dados.pop("registrado_em", None)  # a hora não muda o ferramental
        return dados
    return {}


def montar(raiz):
    tools = {}
    dist = raiz / "dist"
    if dist.exists():
        for arq in sorted(dist.glob("*.pyz")):
            tools[arq.stem] = {"tipo": "pyz", "sha256": sha256(arq)}
    venvs = raiz / "venvs"
    if venvs.exists():
        for pasta in sorted(p for p in venvs.iterdir() if p.is_dir()):
            tools[pasta.name] = {"tipo": "pip", "pacotes": versoes_pip(pasta)}
    corpo = {
        "ambiente": {
            "so": platform.platform(),
            "python": platform.python_version(),
            "maquina": platform.machine(),
        },
        "tools": tools,
    }
    aparelho = dispositivo(raiz)
    if aparelho:
        corpo["dispositivo"] = aparelho
    canonico = json.dumps(corpo, sort_keys=True, ensure_ascii=False).encode()
    return {
        "id": hashlib.sha256(canonico).hexdigest()[:16],
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **corpo,
    }


def verificar(arquivo, atual):
    antigo = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    if antigo["id"] == atual["id"]:
        print(f"OK: ambiente idêntico ao manifesto {antigo['id']}")
        return 0
    print(f"DIFERENTE: manifesto {antigo['id']} x ambiente atual {atual['id']}")
    if antigo.get("dispositivo") != atual.get("dispositivo"):
        print("  - aparelho de coleta: diferente (modelo, sistema, patch ou bootloader)")
    nomes = sorted(set(antigo["tools"]) | set(atual["tools"]))
    for nome in nomes:
        a, b = antigo["tools"].get(nome), atual["tools"].get(nome)
        if a != b:
            print(f"  - {nome}: {'ausente agora' if b is None else 'novo' if a is None else 'alterado'}")
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="trem manifesto", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--saida", help="arquivo JSON de saída")
    p.add_argument("--verificar", metavar="ARQUIVO", help="compara com um manifesto salvo")
    p.add_argument("--base", help="pasta da distro (padrão: $TREM_HOME ou /opt/tocaia)")
    a = p.parse_args(argv)
    atual = montar(Path(a.base) if a.base else base())
    if a.verificar:
        return verificar(a.verificar, atual)
    texto = json.dumps(atual, indent=2, ensure_ascii=False)
    if a.saida:
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
        print(f"manifesto {atual['id']} gravado em {a.saida}")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())

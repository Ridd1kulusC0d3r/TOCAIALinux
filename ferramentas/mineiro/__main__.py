#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MINEIRO — o extrator de identificadores.          DEIVOSINT · TOCAIA · fase C (Cercar)

Lê um texto (arquivo, ou o que você colar no stdin) e extrai os seletores que
servem para pivotar uma investigação, com atenção ao Brasil:

  e-mail · URL · IP · telefone (E.164/BR) · CPF · CNPJ · CEP · @handle · chave PIX

CPF e CNPJ saem VALIDADOS pelos dígitos verificadores (descarta número que só
tem a cara de documento). Cada achado aparece uma vez, com onde apareceu.

Uso:
  mineiro arquivo.txt
  cat relatorio.txt | mineiro -
  mineiro arquivo.txt --json achados.json
  mineiro arquivo.txt --tipo cpf,cnpj,telefone

Só biblioteca padrão. Não acessa a internet: ele lê, não consulta.
"""
import argparse
import json
import re
import sys
from pathlib import Path

VERSAO = "1.0.0"

# --------------------------------------------------------------- padrões

PADROES = {
    "email": re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "url": re.compile(r"\bhttps?://[^\s<>\"')]+", re.I),
    "ip": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "cnpj": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
    "cep": re.compile(r"\b\d{5}-?\d{3}\b"),
    "telefone": re.compile(r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-.\s]?\d{4}\b"),
    "handle": re.compile(r"(?<![\w@])@[A-Za-z0-9_.]{2,30}\b"),
}


def so_digitos(s):
    return re.sub(r"\D", "", s)


def cpf_valido(cpf):
    n = so_digitos(cpf)
    if len(n) != 11 or len(set(n)) == 1:
        return False
    for tam in (9, 10):
        soma = sum(int(n[i]) * ((tam + 1) - i) for i in range(tam))
        dig = (soma * 10) % 11 % 10
        if dig != int(n[tam]):
            return False
    return True


def cnpj_valido(cnpj):
    n = so_digitos(cnpj)
    if len(n) != 14 or len(set(n)) == 1:
        return False
    for tam, pesos in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]),
                       (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        soma = sum(int(n[i]) * pesos[i] for i in range(tam))
        resto = soma % 11
        dig = 0 if resto < 2 else 11 - resto
        if dig != int(n[tam]):
            return False
    return True


def telefone_br(bruto):
    """Normaliza para E.164 se parecer um telefone BR plausível; senão, None."""
    n = so_digitos(bruto)
    if n.startswith("55") and len(n) in (12, 13):
        n = n[2:]
    if len(n) in (10, 11) and n[0] != "0":
        ddd = int(n[:2])
        if 11 <= ddd <= 99:
            return "+55" + n
    return None


def chave_pix(ach):
    """Classifica um achado como possível chave PIX e normaliza."""
    if ach["tipo"] == "email":
        return ach["valor"].lower()
    if ach["tipo"] == "telefone":
        return ach["valor"]  # já E.164
    if ach["tipo"] in ("cpf", "cnpj"):
        return so_digitos(ach["valor"])
    return None


UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)


# --------------------------------------------------------------- extração

def extrair(texto, tipos=None):
    achados = {}  # (tipo, valor_norm) -> dict

    def add(tipo, valor, norm=None, nota=""):
        chave = (tipo, norm or valor)
        if chave in achados:
            achados[chave]["ocorrencias"] += 1
            return
        achados[chave] = {"tipo": tipo, "valor": norm or valor, "bruto": valor,
                          "ocorrencias": 1, "nota": nota}

    for tipo, rx in PADROES.items():
        if tipos and tipo not in tipos:
            continue
        for m in rx.finditer(texto):
            bruto = m.group(0).strip()
            if tipo == "url":
                bruto = bruto.rstrip(".,;:)]}>\"'")
            if tipo == "cpf":
                if cpf_valido(bruto):
                    add("cpf", bruto, so_digitos(bruto), "dígito verificador OK")
            elif tipo == "cnpj":
                if cnpj_valido(bruto):
                    add("cnpj", bruto, so_digitos(bruto), "dígito verificador OK")
            elif tipo == "telefone":
                e164 = telefone_br(bruto)
                if e164:
                    add("telefone", bruto, e164, "BR, E.164")
            elif tipo == "cep":
                add("cep", bruto, so_digitos(bruto))
            elif tipo == "ip":
                add("ip", bruto)
            else:
                add(tipo, bruto)

    # chaves PIX a partir do que já achamos + UUID aleatório
    if not tipos or "pix" in tipos:
        for a in list(achados.values()):
            k = chave_pix(a)
            if k:
                achados.setdefault(("pix", k), {"tipo": "pix", "valor": k, "bruto": a["bruto"],
                                                "ocorrencias": 1, "nota": f"via {a['tipo']}"})
        for m in UUID.finditer(texto):
            achados.setdefault(("pix", m.group(0).lower()),
                               {"tipo": "pix", "valor": m.group(0).lower(), "bruto": m.group(0),
                                "ocorrencias": 1, "nota": "chave aleatória"})

    return sorted(achados.values(), key=lambda a: (a["tipo"], a["valor"]))


# --------------------------------------------------------------- saída

def imprimir(achados, cor=True):
    def c(rgb, s):
        return f"\033[38;2;{rgb}m{s}\033[0m" if cor else s
    menta, ambar, apag = "94;230;196", "244;190;63", "138;150;147"
    if not achados:
        print(c(apag, "Nada encontrado.")); return
    print(c(menta, f"\n◆ MINEIRO — {len(achados)} identificador(es)\n"))
    largura = max(len(a["tipo"]) for a in achados)
    atual = None
    for a in achados:
        if a["tipo"] != atual:
            atual = a["tipo"]
            print(c(ambar, f"  {atual.upper()}"))
        occ = f" ×{a['ocorrencias']}" if a["ocorrencias"] > 1 else ""
        nota = c(apag, f"   ({a['nota']})") if a["nota"] else ""
        print(f"    {a['valor']}{c(apag, occ)}{nota}")
    print(c(apag, "\n  Identificador é ponto de partida, não prova. Pivote e confirme na fonte.\n"))


def main(argv=None):
    p = argparse.ArgumentParser(prog="mineiro", description="MINEIRO — extrator de identificadores (BR).")
    p.add_argument("arquivo", nargs="?", default="-", help="arquivo de texto (ou - para stdin)")
    p.add_argument("--tipo", help="só estes tipos, separados por vírgula "
                                  "(email,url,ip,cpf,cnpj,cep,telefone,handle,pix)")
    p.add_argument("--json", help="grava os achados em JSON")
    p.add_argument("--sem-cor", action="store_true")
    p.add_argument("--version", action="version", version=f"MINEIRO {VERSAO}")
    a = p.parse_args(argv)

    if a.arquivo == "-":
        texto = sys.stdin.read()
    else:
        texto = Path(a.arquivo).read_text(encoding="utf-8", errors="replace")
    tipos = {t.strip() for t in a.tipo.split(",")} if a.tipo else None
    achados = extrair(texto, tipos)
    imprimir(achados, cor=sys.stdout.isatty() and not a.sem_cor)
    if a.json:
        Path(a.json).write_text(json.dumps(achados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✓ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

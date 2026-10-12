"""opsec — checklist de OPSEC do analista antes de abrir o navegador.

Faz checagens LOCAIS e passivas (não manda nada para a internet):
fuso horário, idioma, nome da máquina e do usuário, interface de VPN.
Depois mostra o checklist da fase Observar.

    trem opsec            checagem + checklist
    trem opsec --json     saída em JSON (para anexar ao relatório)
"""
import argparse
import getpass
import json
import locale
import os
import socket
import sys
import time
from pathlib import Path

CHECKLIST = [
    "Pergunta de inteligência e escopo escritos (fase Traçar)",
    "Base legal e limite ético definidos: nada de invadir, enganar ou assediar",
    "Navegador dedicado à investigação, sem suas contas pessoais logadas",
    "Conta-fantoche (sock puppet) separada, se a fonte exigir login",
    "VPN ou rede de saída que não aponte para você ou para a empresa",
    "Fuso e idioma do navegador coerentes com a persona",
    "Nenhuma interação com o alvo: não curtir, não seguir, não mandar mensagem",
    "Capturas com data, hora, URL e hash (use `trem manifesto` no fim)",
]

PISTAS_VPN = ("tun", "tap", "wg", "ppp", "proton", "nord", "mullvad", "utun")


def interfaces():
    pasta = Path("/sys/class/net")
    if pasta.exists():
        return sorted(p.name for p in pasta.iterdir())
    try:
        return sorted(nome for _, nome in socket.if_nameindex())
    except (OSError, AttributeError):
        return []


def checar():
    ifs = interfaces()
    vpn = [i for i in ifs if i.lower().startswith(PISTAS_VPN)]
    usuario = getpass.getuser()
    maquina = socket.gethostname()
    alertas = []
    if not vpn:
        alertas.append("nenhuma interface de VPN aparente (tun/wg/ppp...)")
    if len(usuario) > 3 and usuario.lower() in maquina.lower():
        alertas.append("o nome da máquina contém seu usuário; evite em capturas de tela")
    return {
        "fuso": time.tzname[0],
        "idioma": (locale.getlocale()[0] or os.environ.get("LANG", "desconhecido")),
        "usuario": usuario,
        "maquina": maquina,
        "interfaces": ifs,
        "vpn_aparente": vpn,
        "alertas": alertas,
        "checklist": CHECKLIST,
    }


def main(argv=None):
    p = argparse.ArgumentParser(prog="trem opsec", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", action="store_true", help="saída em JSON")
    a = p.parse_args(argv)
    r = checar()
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0
    print("== Ambiente (checagem local, nada saiu da máquina) ==")
    for chave in ("fuso", "idioma", "usuario", "maquina"):
        print(f"  {chave:8} {r[chave]}")
    print(f"  vpn      {', '.join(r['vpn_aparente']) or 'não aparente'}")
    for alerta in r["alertas"]:
        print(f"  ! {alerta}")
    print("\n== Checklist da fase Observar ==")
    for item in CHECKLIST:
        print(f"  [ ] {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

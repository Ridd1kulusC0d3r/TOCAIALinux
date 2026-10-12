#!/usr/bin/env python3
"""TOCAIA "Matula" — lado do PC: o computador vira a tela do "modo DeX".

Roda no Windows, macOS ou Linux. Só biblioteca padrão do Python.
Precisa de duas ferramentas gratuitas: adb (Android Platform Tools) e scrcpy.

O POCO X6 Pro não tem saída de vídeo pelo cabo (USB 2.0). Então o PC faz o
papel do monitor: o scrcpy 3+ cria um MONITOR VIRTUAL no Android e mostra só
ele numa janela do PC. O celular segue livre, com a própria tela.

Uso:
    python3 tocaia_pc.py              menu interativo (é o que os lançadores abrem)
    python3 tocaia_pc.py checar       confere adb, scrcpy e o celular conectado
    python3 tocaia_pc.py preparar     ajustes de 1ª vez no celular (janelas livres etc.)
    python3 tocaia_pc.py dex          abre o desktop TOCAIA num monitor virtual no PC
    python3 tocaia_pc.py espelhar     espelha a tela do celular (modo simples)
    python3 tocaia_pc.py parear IP:PORTA CODIGO   depuração sem fio (Android 11+)
    python3 tocaia_pc.py conectar IP:PORTA
    python3 tocaia_pc.py reverter     desfaz os ajustes do `preparar`
Qualquer comando aceita --simular.
"""
import argparse
import re
import shutil
import subprocess
import sys

X11_PACOTE = "com.termux.x11"

# Ajustes do `preparar`: (descrição, comando adb shell, comando para reverter)
AJUSTES = [
    ("janelas livres (freeform), como no DeX",
     "settings put global enable_freeform_support 1",
     "settings put global enable_freeform_support 0"),
    ("todo app pode ser redimensionado",
     "settings put global force_resizable_activities 1",
     "settings put global force_resizable_activities 0"),
    ("modo desktop em telas externas e virtuais",
     "settings put global force_desktop_mode_on_external_displays 1",
     "settings put global force_desktop_mode_on_external_displays 0"),
    ("Android 12L+: não matar os processos do Termux",
     "settings put global settings_enable_monitor_phantom_procs false",
     "settings put global settings_enable_monitor_phantom_procs true"),
    ("Android 12: limite de processos filhos bem alto",
     "device_config set_sync_disabled_for_tests persistent && "
     "device_config put activity_manager max_phantom_processes 2147483647",
     "device_config set_sync_disabled_for_tests none && "
     "device_config delete activity_manager max_phantom_processes"),
    ("tela não apaga enquanto estiver no cabo USB",
     "svc power stayon usb",
     "svc power stayon false"),
]


# ---------------------------------------------------------------- utilidades

def rodar(cmd, simular=False, capturar=False):
    print("  $ " + " ".join(cmd))
    if simular:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    try:
        return subprocess.run(cmd, capture_output=capturar, text=True)
    except FileNotFoundError:
        print(f"  não achei '{cmd[0]}'. Rode `tocaia_pc.py checar` para ver como instalar.")
        return subprocess.CompletedProcess(cmd, 127, "", "")


def versao_scrcpy(texto):
    """'scrcpy 4.0 <https://...>' -> (4, 0). Sem versão -> (0, 0)."""
    m = re.search(r"scrcpy\s+(\d+)\.(\d+)", texto or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def celulares(texto_adb_devices):
    """Lê `adb devices` e devolve [(serial, estado)]."""
    lista = []
    for linha in (texto_adb_devices or "").splitlines()[1:]:
        partes = linha.split()
        if len(partes) >= 2:
            lista.append((partes[0], partes[1]))
    return lista


def comando_dex(versao, resolucao="1920x1080", dpi=160, titulo="TOCAIA · Matula"):
    """Monta o scrcpy do 'modo DeX': monitor virtual + Termux:X11 dentro dele."""
    if versao < (3, 0):
        raise ValueError("o monitor virtual precisa do scrcpy 3.0 ou mais novo")
    cmd = ["scrcpy", f"--new-display={resolucao}/{dpi}", f"--start-app={X11_PACOTE}",
           f"--window-title={titulo}", "--stay-awake", "-b", "16M"]
    if versao >= (4, 0):
        cmd.append("--flex-display")   # 4.0+: janela redimensionável como app de PC
    return cmd


def comando_espelhar(titulo="TOCAIA · espelho"):
    return ["scrcpy", f"--window-title={titulo}", "--stay-awake", "-b", "8M"]


# ---------------------------------------------------------------- comandos

DICAS = {
    "adb": "Android Platform Tools: https://developer.android.com/tools/releases/platform-tools "
           "(Windows: winget install Google.PlatformTools · Mac: brew install android-platform-tools "
           "· Linux: sudo apt install adb)",
    "scrcpy": "scrcpy: https://github.com/Genymobile/scrcpy (Windows: winget install Genymobile.scrcpy "
              "· Mac: brew install scrcpy · Linux: baixe do GitHub, versão 3.0 ou mais nova)",
}


def checar():
    ok = True
    for nome in ("adb", "scrcpy"):
        achou = shutil.which(nome)
        print(f"  {'ok ' if achou else '-- '} {nome:8} {achou or DICAS[nome]}")
        ok = ok and bool(achou)
    if shutil.which("scrcpy"):
        v = versao_scrcpy(subprocess.run(["scrcpy", "--version"], capture_output=True,
                                         text=True).stdout)
        print(f"      scrcpy {v[0]}.{v[1]} — "
              + ("monitor virtual redimensionável" if v >= (4, 0) else
                 "monitor virtual" if v >= (3, 0) else "ANTIGO: atualize para 3.0+"))
        ok = ok and v >= (3, 0)
    if shutil.which("adb"):
        aparelhos = celulares(subprocess.run(["adb", "devices"], capture_output=True,
                                             text=True).stdout)
        if not aparelhos:
            print("  --  celular  nenhum. Ligue a Depuração USB e conecte o cabo.")
            ok = False
        for serial, estado in aparelhos:
            marca = "ok " if estado == "device" else "-- "
            dica = "" if estado == "device" else "aceite a chave RSA na tela do celular"
            print(f"  {marca} celular  {serial} ({estado}) {dica}")
            ok = ok and estado == "device"
    return 0 if ok else 1


def preparar(simular=False, reverter=False):
    print("\nAjustes no celular (reversíveis com `tocaia_pc.py reverter`):\n")
    for desc, ligar, desligar in AJUSTES:
        print(f"• {desc}")
        rodar(["adb", "shell", desligar if reverter else ligar], simular)
    print("\nPronto. Reinicie o celular uma vez para as janelas livres valerem em tudo.")
    return 0


def dex(simular=False, resolucao="1920x1080", dpi=160):
    texto = "scrcpy 4.0" if simular else subprocess.run(
        ["scrcpy", "--version"], capture_output=True, text=True).stdout
    try:
        cmd = comando_dex(versao_scrcpy(texto), resolucao, dpi)
    except ValueError as erro:
        print(f"  {erro}. {DICAS['scrcpy']}")
        return 1
    print("\nAbrindo o desktop TOCAIA num monitor virtual no PC.")
    print("Antes, toque em 'TOCAIA Desktop' no celular (ou rode `tocaia_celular.py desktop`).\n")
    return rodar(cmd, simular).returncode


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        return menu()
    p = argparse.ArgumentParser(prog="tocaia_pc.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("comando", choices=["checar", "preparar", "reverter", "dex", "espelhar",
                                       "parear", "conectar"])
    p.add_argument("alvo", nargs="*", help="IP:PORTA [CODIGO] para parear/conectar")
    p.add_argument("--resolucao", default="1920x1080", help="tamanho do monitor virtual")
    p.add_argument("--dpi", type=int, default=160, help="densidade (maior = letras maiores)")
    p.add_argument("--simular", action="store_true")
    a = p.parse_args(argv)
    if a.comando == "checar":
        return checar()
    if a.comando in ("preparar", "reverter"):
        return preparar(a.simular, reverter=a.comando == "reverter")
    if a.comando == "dex":
        return dex(a.simular, a.resolucao, a.dpi)
    if a.comando == "espelhar":
        return rodar(comando_espelhar(), a.simular).returncode
    if a.comando == "parear":
        if len(a.alvo) != 2:
            print("uso: tocaia_pc.py parear IP:PORTA CODIGO  (veja em Depuração sem fio → "
                  "Parear com código)")
            return 2
        return rodar(["adb", "pair", *a.alvo], a.simular).returncode
    if len(a.alvo) != 1:
        print("uso: tocaia_pc.py conectar IP:PORTA  (a porta da tela Depuração sem fio)")
        return 2
    return rodar(["adb", "connect", a.alvo[0]], a.simular).returncode


MENU = [("checar", "conferir adb, scrcpy e o celular"),
        ("preparar", "ajustes de 1ª vez no celular"),
        ("dex", "abrir o desktop TOCAIA no PC (modo DeX)"),
        ("espelhar", "só espelhar a tela do celular"),
        ("reverter", "desfazer os ajustes")]


def menu():
    print('\n  TOCAIA "Matula" — o PC como tela do celular\n')
    for i, (cmd, desc) in enumerate(MENU, 1):
        print(f"  {i}. {desc}")
    escolha = input("\n  número: ").strip()
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(MENU):
        print("  opção inválida")
        return 2
    return main([MENU[int(escolha) - 1][0]])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nfalou, até mais.")
        sys.exit(130)

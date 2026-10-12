#!/usr/bin/env python3
"""TOCAIA "Matula" — a edição de bolso da TOCAIA OSINT Linux, para Android.

Roda dentro do Termux. Só biblioteca padrão do Python.

Recria as 4 peças do "modo DeX" com peças abertas:
  1. Linux de verdade ...... Debian 13 (proot-distro) com Xfce e o tema TOCAIA
  2. Tela gráfica .......... Termux:X11
  3. Janelas e barra ....... Xfce dentro do X11 (e janelas livres do Android)
  4. Tela grande ........... o próprio celular, o PC (scrcpy) ou a TV (Miracast)

Uso:
    python tocaia_celular.py                 menu interativo
    python tocaia_celular.py doutor          confere se o celular está pronto
    python tocaia_celular.py instalar        instala tudo (sem root)
    python tocaia_celular.py desktop         abre o desktop TOCAIA (sem root)
    python tocaia_celular.py desktop --root  abre pelo chroot (precisa de root)
    python tocaia_celular.py desktop --tela tv   abre e chama o espelhamento
    python tocaia_celular.py parar           fecha o desktop
    python tocaia_celular.py atalhos         cria os botões na tela inicial
    python tocaia_celular.py dispositivo     grava a ficha do aparelho
Qualquer comando aceita --simular: mostra o que faria, sem fazer.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VERSAO = "1.0.0"
CODINOME = "Matula"
DISTRO = "debian"            # alias do proot-distro (Debian 13 "trixie")
USUARIO = "analista"
DISPLAY = ":0"
X11_APP = "com.termux.x11/com.termux.x11.MainActivity"

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent           # raiz do repositório TOCAIALinux
PREFIX = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))
HOME = Path(os.environ.get("HOME", str(Path.home())))

# Pacotes do lado Termux (Android)
PACOTES_TERMUX = ["termux-x11-nightly", "proot-distro", "git", "python", "termux-api"]

# A lista de pacotes do Debian sai da MESMA lista da ISO: uma fonte só.
# Tiramos o que não faz sentido dentro do celular.
LISTA_ISO = RAIZ / "iso/config/package-lists/tocaia.list.chroot"
FORA_DO_CELULAR = {
    "live-boot", "live-config", "live-config-systemd",       # é coisa de pendrive
    "lightdm", "lightdm-gtk-greeter",                         # o Termux:X11 é a tela
    "network-manager-gnome",                                  # quem cuida da rede é o Android
    "firmware-linux-free", "firmware-iwlwifi", "firmware-realtek",  # hardware é do Android
    "torbrowser-launcher",                                    # sem build oficial para ARM
}
EXTRAS_CELULAR = ["dbus-x11", "xfce4-notifyd", "at-spi2-core", "tzdata"]

# Propriedades do Android que entram na ficha do aparelho (cadeia de custódia)
PROPS = {
    "ro.product.manufacturer": "fabricante",
    "ro.product.marketname": "nome_comercial",
    "ro.product.model": "modelo",
    "ro.product.device": "codinome",
    "ro.build.version.release": "android",
    "ro.build.version.incremental": "build",
    "ro.build.version.security_patch": "patch_seguranca",
    "ro.build.fingerprint": "fingerprint",
    "ro.boot.verifiedbootstate": "verified_boot",
    "ro.boot.flash.locked": "bootloader_travado",
    "ro.product.cpu.abi": "abi",
}


# ---------------------------------------------------------------- caminhos

def rootfs():
    """Onde o proot-distro guarda o Debian (o mesmo serve para o chroot)."""
    return PREFIX / "var/lib/proot-distro/installed-rootfs" / DISTRO


SU_CAMINHOS = ["/system/bin/su", "/system/xbin/su", "/sbin/su", "/debug_ramdisk/su",
               "/data/adb/ksu/bin/su", "/data/adb/magisk/su"]


def achar_su():
    """Caminho do `su` do Android (Magisk/KernelSU), ou None se não há root."""
    for caminho in SU_CAMINHOS:
        if os.path.exists(caminho):
            return caminho
    return None


def tmp_termux():
    """A /tmp do Termux: é onde o Termux:X11 cria o socket da tela :0."""
    return PREFIX / "tmp"


# ---------------------------------------------------------------- passos

class Passo:
    """Um passo do plano. 'cmd' é uma lista (comando) ou uma função Python."""

    def __init__(self, titulo, cmd, fundo=False, pode_falhar=False):
        self.titulo, self.cmd = titulo, cmd
        self.fundo, self.pode_falhar = fundo, pode_falhar

    def texto(self):
        if callable(self.cmd):
            return f"(python) {self.cmd.__name__}"
        return " ".join(self.cmd)


def executar(passos, simular=False):
    """Roda os passos em ordem. Para no primeiro erro (salvo 'pode_falhar')."""
    for i, p in enumerate(passos, 1):
        print(f"\n[{i}/{len(passos)}] {p.titulo}")
        print(f"      $ {p.texto()}")
        if simular:
            continue
        if callable(p.cmd):
            p.cmd()
            continue
        if p.fundo:
            subprocess.Popen(p.cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            continue
        codigo = subprocess.call(p.cmd)
        if codigo != 0 and not p.pode_falhar:
            print(f"\nuai, sô: o passo {i} falhou (código {codigo}). "
                  "Rode `python tocaia_celular.py doutor` para ver o que falta.")
            return codigo
    return 0


# ---------------------------------------------------------------- pacotes

def pacotes_debian(lista=LISTA_ISO):
    """Lê a lista da ISO, tira o que não serve no celular e soma os extras."""
    nomes = []
    for linha in Path(lista).read_text(encoding="utf-8").splitlines():
        linha = linha.split("#", 1)[0].strip()
        if linha and linha not in FORA_DO_CELULAR and linha not in nomes:
            nomes.append(linha)
    for extra in EXTRAS_CELULAR:
        if extra not in nomes:
            nomes.append(extra)
    return nomes


# ---------------------------------------------------------------- ficha do aparelho

def ler_props(texto):
    """Converte a saída do `getprop` ('[chave]: [valor]') num dicionário."""
    props = {}
    for linha in texto.splitlines():
        if not linha.startswith("[") or "]: [" not in linha:
            continue
        chave, valor = linha[1:].split("]: [", 1)
        props[chave] = valor.rstrip("]")
    return props


def getprop_bruto():
    exe = shutil.which("getprop") or "/system/bin/getprop"
    try:
        return subprocess.run([exe], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def ficha_dispositivo(texto_getprop=None):
    """Ficha do aparelho de coleta: modelo, Android, patch e estado do bootloader."""
    props = ler_props(getprop_bruto() if texto_getprop is None else texto_getprop)
    ficha = {nome: props[chave] for chave, nome in PROPS.items() if chave in props}
    if not ficha:
        return {}
    ficha["registrado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ficha["edicao"] = f"TOCAIA {VERSAO} \"{CODINOME}\""
    return ficha


def gravar_ficha(destino=None, texto_getprop=None):
    """Grava /opt/tocaia/dispositivo.json dentro do Debian (o manifesto lê de lá)."""
    ficha = ficha_dispositivo(texto_getprop)
    alvo = Path(destino) if destino else rootfs() / "opt/tocaia/dispositivo.json"
    if not ficha:
        print("sem getprop aqui (não é Android?): ficha do aparelho não gravada")
        return None
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(json.dumps(ficha, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ficha do aparelho gravada em {alvo}")
    return alvo


# ---------------------------------------------------------------- copiar a TOCAIA

def preparar_rootfs(destino=None):
    """Copia a TOCAIA para dentro do Debian e gera tema e menu por fases.

    É o mesmo conteúdo da ISO: trem, catálogo, tools .pyz, war game, tema e menu.
    """
    raiz = Path(destino) if destino else rootfs()
    opt = raiz / "opt/tocaia"
    subprocess.run([sys.executable, str(RAIZ / "build.py")], check=True,
                   stdout=subprocess.DEVNULL)
    (opt / "dist").mkdir(parents=True, exist_ok=True)
    (opt / "venvs").mkdir(parents=True, exist_ok=True)
    for pyz in (RAIZ / "dist").glob("*.pyz"):
        shutil.copy2(pyz, opt / "dist" / pyz.name)
    shutil.copy2(RAIZ / "catalogo.json", opt / "catalogo.json")
    if (opt / "wargames").exists():
        shutil.rmtree(opt / "wargames")
    shutil.copytree(RAIZ / "wargames", opt / "wargames")
    bin_ = raiz / "usr/local/bin"
    bin_.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RAIZ / "trem/trem.py", bin_ / "trem")
    shutil.copy2(AQUI / "rootfs/tocaia-papel-de-parede", bin_ / "tocaia-papel-de-parede")
    perfil = raiz / "etc/profile.d"
    perfil.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RAIZ / "container/tocaia-profile.sh", perfil / "tocaia.sh")
    auto = raiz / "etc/xdg/autostart"
    auto.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AQUI / "rootfs/tocaia-papel-de-parede.desktop", auto / "tocaia-papel-de-parede.desktop")
    for script in ("tema/gerar_tema.py", "iso/gerar_menu.py"):
        subprocess.run([sys.executable, str(RAIZ / script), str(raiz)], check=True,
                       stdout=subprocess.DEVNULL)
    shutil.copy2(AQUI / "rootfs/tocaia-setup.sh", opt / "tocaia-setup.sh")
    print(f"TOCAIA copiada para {raiz} (trem, {len(list((opt / 'dist').glob('*.pyz')))} tools, tema, menu)")
    return raiz


# ---------------------------------------------------------------- planos

def plano_instalar(tem_rootfs=None):
    """Instala o lado Android, o Debian, os pacotes e a TOCAIA."""
    if tem_rootfs is None:
        tem_rootfs = rootfs().exists()
    passos = [
        Passo("atualizar o Termux", ["pkg", "upgrade", "-y"]),
        Passo("ligar o repositório gráfico (x11-repo)", ["pkg", "install", "-y", "x11-repo"]),
        Passo("instalar Termux:X11, proot-distro e Python", ["pkg", "install", "-y", *PACOTES_TERMUX]),
    ]
    if not tem_rootfs:
        passos.append(Passo("baixar o Debian 13 (uns 100 MB)", ["proot-distro", "install", DISTRO]))
    pacotes = " ".join(pacotes_debian())
    passos += [
        Passo("instalar Xfce e a base OSINT dentro do Debian (demora: ~1 GB)",
              ["proot-distro", "login", DISTRO, "--", "bash", "-c",
               "apt-get update && DEBIAN_FRONTEND=noninteractive "
               f"apt-get install -y --no-install-recommends {pacotes}"]),
        Passo("copiar trem, tools, tema e menu da TOCAIA", preparar_rootfs),
        Passo("criar o usuário analista, idioma e fuso",
              ["proot-distro", "login", DISTRO, "--", "bash", "/opt/tocaia/tocaia-setup.sh", USUARIO]),
        Passo("registrar a ficha do aparelho", gravar_ficha),
    ]
    return passos


def plano_desktop(root=False, tela="celular", legado=False, bgra=False):
    """Sobe a tela X11 e a sessão Xfce, por proot (sem root) ou chroot (com root)."""
    passos = [
        Passo("fechar sessão anterior", ["pkill", "-f", "com.termux.x11"], pode_falhar=True),
        Passo("atualizar a ficha do aparelho", gravar_ficha),
        Passo("ligar o servidor gráfico Termux:X11",
              ["termux-x11", DISPLAY, *(["-legacy-drawing"] if legado else []),
               *(["-force-bgra"] if bgra else [])], fundo=True),
        Passo("abrir o app Termux:X11", ["am", "start", "--user", "0", "-n", X11_APP]),
    ]
    if tela == "tv":
        passos.append(Passo("abrir o espelhamento sem fio (escolha a TV)",
                            ["am", "start", "-a", "android.settings.CAST_SETTINGS"],
                            pode_falhar=True))
    sessao = f"export DISPLAY={DISPLAY}; dbus-launch --exit-with-session xfce4-session"
    if root:
        passos.append(Passo("entrar no Debian pelo chroot (root) e abrir o Xfce",
                            [achar_su() or "su", "-c", f"sh {AQUI / 'chroot/entrar-chroot.sh'} "
                                         f"{rootfs()} {tmp_termux()} {USUARIO}"]))
    else:
        passos.append(Passo("entrar no Debian pelo proot (sem root) e abrir o Xfce",
                            ["proot-distro", "login", DISTRO, "--shared-tmp", "--user", USUARIO,
                             "--", "bash", "-lc", sessao]))
    return passos


def plano_parar(root=False):
    passos = [
        Passo("fechar o app Termux:X11",
              ["am", "broadcast", "-a", "com.termux.x11.ACTION_STOP", "-p", "com.termux.x11"],
              pode_falhar=True),
        Passo("encerrar o servidor gráfico", ["pkill", "-f", "termux-x11"], pode_falhar=True),
    ]
    if root:
        passos.append(Passo("desmontar o chroot",
                            [achar_su() or "su", "-c", f"sh {AQUI / 'chroot/sair-chroot.sh'} {rootfs()}"],
                            pode_falhar=True))
    else:
        passos.append(Passo("encerrar o proot", ["pkill", "-f", "proot"], pode_falhar=True))
    return passos


def instalar_atalhos(destino=None):
    """Copia os botões do Termux:Widget para ~/.shortcuts (um toque na tela inicial)."""
    pasta = Path(destino) if destino else HOME / ".shortcuts"
    pasta.mkdir(parents=True, exist_ok=True)
    feitos = []
    for origem in sorted((AQUI / "atalhos").iterdir()):
        alvo = pasta / origem.name
        texto = origem.read_text(encoding="utf-8").replace("@TOCAIA@", str(AQUI))
        alvo.write_text(texto, encoding="utf-8")
        alvo.chmod(0o755)
        feitos.append(alvo.name)
    print(f"{len(feitos)} atalhos em {pasta}: {', '.join(feitos)}")
    print("Agora, na tela inicial: segure num espaço vazio → Widgets → Termux:Widget.")
    return feitos


# ---------------------------------------------------------------- doutor

def versao_android(props):
    """'15' -> 15; '8.1.0' -> 8; ausente -> 0."""
    principal = props.get("ro.build.version.release", "").split(".")[0]
    return int(principal) if principal.isdigit() else 0


def doutor(texto_getprop=None):
    """Checa o que está pronto. Devolve a lista de (item, ok, dica)."""
    props = ler_props(getprop_bruto() if texto_getprop is None else texto_getprop)
    no_termux = "com.termux" in os.environ.get("PREFIX", "")
    try:
        livre_gb = shutil.disk_usage(HOME).free / 1e9
    except OSError:
        livre_gb = 0
    itens = [
        ("dentro do Termux", no_termux, "instale o Termux pelo F-Droid ou GitHub"),
        ("processador ARM 64 bits", platform.machine() in ("aarch64", "arm64"),
         f"achei {platform.machine()}"),
        ("Android 10 ou mais novo", versao_android(props) >= 10,
         f"Android {props.get('ro.build.version.release', '?')}"),
        ("3 GB livres ou mais", livre_gb >= 3, f"{livre_gb:.1f} GB livres"),
        ("Termux:X11 (pacote)", shutil.which("termux-x11") is not None, "rode: instalar"),
        ("proot-distro", shutil.which("proot-distro") is not None, "rode: instalar"),
        ("Debian instalado", rootfs().exists(), "rode: instalar"),
        ("TOCAIA dentro do Debian", (rootfs() / "opt/tocaia/catalogo.json").exists(), "rode: instalar"),
        ("root (opcional)", achar_su() is not None, "sem root: use o modo proot"),
    ]
    modelo = props.get("ro.product.model", "?")
    print(f"\nTOCAIA {VERSAO} \"{CODINOME}\" — doutor · aparelho: {modelo} "
          f"({props.get('ro.product.device', '?')})\n")
    for nome, ok, dica in itens:
        print(f"  {'ok ' if ok else '-- '} {nome:28} {'' if ok else dica}")
    print("\nDica: se o desktop fechar sozinho, rode no PC `tocaia_pc.py preparar` "
          "(desliga o limitador de processos do Android 12+).")
    return itens


# ---------------------------------------------------------------- menu

MENU = [
    ("doutor", "conferir se o celular está pronto"),
    ("instalar", "instalar tudo (sem root)"),
    ("desktop", "abrir o desktop TOCAIA na tela do celular"),
    ("desktop --root", "abrir pelo chroot (com root, mais rápido)"),
    ("desktop --tela tv", "abrir e espelhar na TV"),
    ("atalhos", "criar os botões na tela inicial"),
    ("parar", "fechar o desktop"),
]


def menu_interativo():
    print(f"\n  uai, sô — TOCAIA \"{CODINOME}\": a matula do tropeiro, no bolso.\n")
    for i, (cmd, desc) in enumerate(MENU, 1):
        print(f"  {i}. {desc:45} ({cmd})")
    escolha = input("\n  número: ").strip()
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(MENU):
        print("  opção inválida")
        return 2
    return main(MENU[int(escolha) - 1][0].split())


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        return menu_interativo()
    p = argparse.ArgumentParser(prog="tocaia_celular.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("comando", choices=["doutor", "instalar", "desktop", "parar",
                                       "atalhos", "dispositivo", "versao"])
    p.add_argument("--root", action="store_true", help="usar chroot (precisa de root)")
    p.add_argument("--tela", choices=["celular", "pc", "tv"], default="celular")
    p.add_argument("--legacy", action="store_true", help="tela preta só com cursor? use isto")
    p.add_argument("--bgra", action="store_true", help="cores trocadas? use isto")
    p.add_argument("--simular", action="store_true", help="mostrar sem executar")
    a = p.parse_args(argv)

    if a.comando == "versao":
        print(f"TOCAIA {VERSAO} \"{CODINOME}\" — edição Android")
        return 0
    if a.comando == "doutor":
        doutor()
        return 0
    if a.comando == "atalhos":
        instalar_atalhos()
        return 0
    if a.comando == "dispositivo":
        return 0 if gravar_ficha() else 1
    if a.comando == "instalar":
        return executar(plano_instalar(), a.simular)
    if a.comando == "parar":
        return executar(plano_parar(a.root), a.simular)
    if a.tela == "pc":
        print("Tela no PC: depois que o desktop abrir, rode no computador "
              "`python3 tocaia_pc.py dex` (ou dois cliques no lançador TOCAIA-DeX).")
    return executar(plano_desktop(a.root, a.tela, a.legacy, a.bgra), a.simular)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nfalou, até mais.")
        sys.exit(130)

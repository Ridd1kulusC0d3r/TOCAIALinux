"""Testes da edição Android "Matula" (celular/). Só stdlib.

Não há celular na nuvem: os testes conferem os PLANOS (que comandos seriam
rodados), a cópia da TOCAIA para dentro de um Debian simulado, a ficha do
aparelho e a montagem dos comandos do scrcpy.
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carregar(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


celular = carregar("celular/tocaia_celular.py", "tocaia_celular")
pc = carregar("celular/pc/tocaia_pc.py", "tocaia_pc")
manifesto = carregar("tools/manifesto/__main__.py", "manifesto_celular")

GETPROP_POCO = """[ro.product.manufacturer]: [Xiaomi]
[ro.product.marketname]: [POCO X6 Pro 5G]
[ro.product.model]: [2311DRK48G]
[ro.product.device]: [duchamp]
[ro.build.version.release]: [15]
[ro.build.version.incremental]: [OS2.0.6.0.VNLMIXM]
[ro.build.version.security_patch]: [2026-08-01]
[ro.boot.verifiedbootstate]: [green]
[ro.boot.flash.locked]: [1]
[ro.product.cpu.abi]: [arm64-v8a]
[persist.sys.algo.nao.interessa]: [x]
linha quebrada sem colchete
"""


UTF8 = dict(os.environ, PYTHONIOENCODING="utf-8")


def silencioso(func, *args, **kw):
    with redirect_stdout(io.StringIO()):
        return func(*args, **kw)


class TestPacotes(unittest.TestCase):
    def test_reaproveita_a_lista_da_iso(self):
        pacotes = celular.pacotes_debian()
        for essencial in ("xfce4-session", "xfce4-terminal", "python3", "firefox-esr",
                          "fonts-inter", "exiftool"):
            self.assertIn(essencial, pacotes)

    def test_tira_o_que_nao_serve_no_celular(self):
        pacotes = celular.pacotes_debian()
        for fora in ("live-boot", "lightdm", "firmware-iwlwifi", "network-manager-gnome",
                     "torbrowser-launcher"):
            self.assertNotIn(fora, pacotes)

    def test_extras_e_sem_repeticao(self):
        pacotes = celular.pacotes_debian()
        self.assertIn("dbus-x11", pacotes)
        self.assertEqual(len(pacotes), len(set(pacotes)))


class TestPlanos(unittest.TestCase):
    def textos(self, passos):
        return [p.texto() for p in passos]

    def test_instalar_baixa_debian_so_se_faltar(self):
        sem = " | ".join(self.textos(celular.plano_instalar(tem_rootfs=False)))
        com = " | ".join(self.textos(celular.plano_instalar(tem_rootfs=True)))
        self.assertIn("proot-distro install debian", sem)
        self.assertNotIn("proot-distro install debian", com)
        self.assertIn("termux-x11-nightly", sem)
        self.assertIn("x11-repo", sem)

    def test_desktop_sem_root_usa_proot_com_tmp_compartilhado(self):
        texto = " | ".join(self.textos(celular.plano_desktop()))
        self.assertIn("--shared-tmp", texto)
        self.assertIn("--user analista", texto)
        self.assertIn("xfce4-session", texto)
        self.assertIn("termux-x11 :0", texto)
        self.assertNotIn("su -c", texto)

    def test_desktop_com_root_usa_chroot(self):
        texto = " | ".join(self.textos(celular.plano_desktop(root=True)))
        self.assertIn(" -c ", texto)
        self.assertIn("entrar-chroot.sh", texto)
        self.assertNotIn("proot-distro login", texto)

    def test_tela_tv_abre_espelhamento(self):
        tv = " | ".join(self.textos(celular.plano_desktop(tela="tv")))
        normal = " | ".join(self.textos(celular.plano_desktop()))
        self.assertIn("CAST_SETTINGS", tv)
        self.assertNotIn("CAST_SETTINGS", normal)

    def test_simular_nao_executa(self):
        chamado = []
        passos = [celular.Passo("teste", lambda: chamado.append(1)),
                  celular.Passo("comando", ["comando-que-nao-existe-123"])]
        self.assertEqual(silencioso(celular.executar, passos, True), 0)
        self.assertEqual(chamado, [])

    def test_para_no_primeiro_erro(self):
        passos = [celular.Passo("falha", [sys.executable, "-c", "import sys; sys.exit(3)"]),
                  celular.Passo("nunca", [sys.executable, "-c", "raise SystemExit(9)"])]
        self.assertEqual(silencioso(celular.executar, passos), 3)

    def test_pode_falhar_segue(self):
        passos = [celular.Passo("ok falhar", [sys.executable, "-c", "raise SystemExit(1)"],
                                pode_falhar=True),
                  celular.Passo("segue", [sys.executable, "-c", "pass"])]
        self.assertEqual(silencioso(celular.executar, passos), 0)

    def test_cli_simulada(self):
        r = subprocess.run([sys.executable, str(RAIZ / "celular/tocaia_celular.py"),
                            "desktop", "--root", "--simular"],
                           capture_output=True, text=True, encoding="utf-8", env=UTF8)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("entrar-chroot.sh", r.stdout)


class TestFichaDoAparelho(unittest.TestCase):
    def test_ler_getprop(self):
        props = celular.ler_props(GETPROP_POCO)
        self.assertEqual(props["ro.product.device"], "duchamp")
        self.assertEqual(props["ro.build.version.release"], "15")
        self.assertEqual(len(props), 11)

    def test_versao_android(self):
        self.assertEqual(celular.versao_android({"ro.build.version.release": "8.1.0"}), 8)
        self.assertEqual(celular.versao_android({}), 0)

    def test_ficha_so_com_campos_escolhidos(self):
        ficha = celular.ficha_dispositivo(GETPROP_POCO)
        self.assertEqual(ficha["codinome"], "duchamp")
        self.assertEqual(ficha["verified_boot"], "green")
        self.assertEqual(ficha["bootloader_travado"], "1")
        self.assertNotIn("persist.sys.algo.nao.interessa", json.dumps(ficha))

    def test_fora_do_android_nao_grava(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "dispositivo.json"
            self.assertIsNone(silencioso(celular.gravar_ficha, alvo, ""))
            self.assertFalse(alvo.exists())

    def test_manifesto_inclui_o_aparelho(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            shutil.copytree(RAIZ / "dist", base / "dist")
            sem = manifesto.montar(base)
            silencioso(celular.gravar_ficha, base / "dispositivo.json", GETPROP_POCO)
            com = manifesto.montar(base)
            self.assertNotIn("dispositivo", sem)
            self.assertEqual(com["dispositivo"]["codinome"], "duchamp")
            self.assertNotEqual(sem["id"], com["id"])
            # a hora do registro não muda o ID; o bootloader destravado muda
            silencioso(celular.gravar_ficha, base / "dispositivo.json", GETPROP_POCO)
            self.assertEqual(manifesto.montar(base)["id"], com["id"])
            silencioso(celular.gravar_ficha, base / "dispositivo.json",
                       GETPROP_POCO.replace("[ro.boot.flash.locked]: [1]",
                                            "[ro.boot.flash.locked]: [0]"))
            self.assertNotEqual(manifesto.montar(base)["id"], com["id"])


class TestRootfs(unittest.TestCase):
    """Simula o Debian do celular numa pasta e roda o trem lá dentro."""

    def test_copia_e_roda(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = silencioso(celular.preparar_rootfs, tmp)
            opt = raiz / "opt/tocaia"
            for rel in ("catalogo.json", "dist/placar.pyz", "tocaia-setup.sh",
                        "wargames/demo/alerts-demo.json"):
                self.assertTrue((opt / rel).exists(), rel)
            for rel in ("usr/local/bin/trem", "usr/local/bin/tocaia-papel-de-parede",
                        "etc/profile.d/tocaia.sh", "etc/xdg/autostart/tocaia-papel-de-parede.desktop",
                        "etc/skel/.config/gtk-3.0/gtk.css",
                        "usr/share/backgrounds/tocaia/tocaia.svg",
                        "etc/xdg/menus/applications-merged/tocaia.menu"):
                self.assertTrue((raiz / rel).exists(), rel)
            env = dict(os.environ, TREM_HOME=str(opt), PYTHONIOENCODING="utf-8")
            r = subprocess.run([sys.executable, str(raiz / "usr/local/bin/trem"), "placar",
                                str(opt / "wargames/cenarios/rodada1-tropeiro-x-atalaia.json"),
                                str(opt / "wargames/demo/alerts-demo.json")],
                               capture_output=True, text=True, encoding="utf-8", env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Vencedor", r.stdout)

    def test_atalhos(self):
        with tempfile.TemporaryDirectory() as tmp:
            feitos = silencioso(celular.instalar_atalhos, tmp)
            self.assertIn("TOCAIA Desktop", feitos)
            texto = (Path(tmp) / "TOCAIA Desktop").read_text(encoding="utf-8")
            self.assertNotIn("@TOCAIA@", texto)
            self.assertIn(str(RAIZ / "celular"), texto)

    @unittest.skipIf(shutil.which("sh") is None or os.name == "nt", "precisa de sh")
    def test_sintaxe_dos_scripts(self):
        scripts = ["celular/instalar.sh", "celular/chroot/entrar-chroot.sh",
                   "celular/chroot/sair-chroot.sh", "celular/rootfs/tocaia-setup.sh",
                   "celular/rootfs/tocaia-papel-de-parede", "celular/pc/TOCAIA-DeX (Linux).sh",
                   *[str(p.relative_to(RAIZ)) for p in (RAIZ / "celular/atalhos").iterdir()]]
        for rel in scripts:
            r = subprocess.run(["sh", "-n", str(RAIZ / rel)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{rel}: {r.stderr}")


class TestPC(unittest.TestCase):
    def test_versao_scrcpy(self):
        self.assertEqual(pc.versao_scrcpy("scrcpy 4.0 <https://github.com/Genymobile/scrcpy>"), (4, 0))
        self.assertEqual(pc.versao_scrcpy("scrcpy 3.3.1"), (3, 3))
        self.assertEqual(pc.versao_scrcpy("nada"), (0, 0))

    def test_dex_monitor_virtual(self):
        cmd = pc.comando_dex((3, 3))
        self.assertIn("--new-display=1920x1080/160", cmd)
        self.assertIn("--start-app=com.termux.x11", cmd)
        self.assertNotIn("--flex-display", cmd)
        self.assertIn("--flex-display", pc.comando_dex((4, 0)))

    def test_dex_recusa_scrcpy_antigo(self):
        with self.assertRaises(ValueError):
            pc.comando_dex((2, 7))

    def test_adb_devices(self):
        saida = "List of devices attached\nabc123\tdevice\n192.168.0.5:41234\tunauthorized\n\n"
        self.assertEqual(pc.celulares(saida), [("abc123", "device"),
                                               ("192.168.0.5:41234", "unauthorized")])

    def test_preparar_e_reversivel(self):
        for desc, ligar, desligar in pc.AJUSTES:
            self.assertNotEqual(ligar, desligar, desc)
        saida = io.StringIO()
        with redirect_stdout(saida):
            pc.preparar(simular=True)
        self.assertIn("enable_freeform_support 1", saida.getvalue())

    def test_cli_dex_simulada(self):
        r = subprocess.run([sys.executable, str(RAIZ / "celular/pc/tocaia_pc.py"), "dex",
                            "--simular", "--resolucao", "2560x1440", "--dpi", "200"],
                           capture_output=True, text=True, encoding="utf-8", env=UTF8)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--new-display=2560x1440/200", r.stdout)


if __name__ == "__main__":
    unittest.main()

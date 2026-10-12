"""Testes da TOCAIA OSINT Linux. Só stdlib:  python3 -m unittest discover -s testes -v"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CENARIO = RAIZ / "wargames/cenarios/rodada1-tropeiro-x-atalaia.json"
DEMO = RAIZ / "wargames/demo/alerts-demo.json"
CATALOGO = json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))


def carregar(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


placar = carregar("tools/placar/__main__.py", "placar")
silencio = carregar("tools/silencio/__main__.py", "silencio")
manifesto = carregar("tools/manifesto/__main__.py", "manifesto")
opsec = carregar("tools/opsec/__main__.py", "opsec")
menu = carregar("iso/gerar_menu.py", "gerar_menu")
tema = carregar("tema/gerar_tema.py", "gerar_tema")


def trem(*args, base=RAIZ):
    env = dict(os.environ, TREM_HOME=str(base), PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, str(RAIZ / "trem/trem.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env)


class TestCatalogo(unittest.TestCase):
    def test_fases_validas(self):
        for nome, t in CATALOGO.items():
            self.assertIn(t["fase"], menu.FASES, nome)

    def test_pyz_tem_codigo(self):
        for nome, t in CATALOGO.items():
            if t["tipo"] == "pyz":
                self.assertTrue((RAIZ / "tools" / nome / "__main__.py").exists(), nome)
                self.assertTrue((RAIZ / "dist" / t["arquivo"]).exists(), f"{nome}: rode build.py")

    def test_pip_completo(self):
        for nome, t in CATALOGO.items():
            if t["tipo"] == "pip":
                self.assertTrue(t.get("pip") and t.get("comando"), nome)


class TestTrem(unittest.TestCase):
    def test_lista_por_fase(self):
        r = trem()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("uai, sô", r.stdout)
        self.assertLess(r.stdout.index("[OBSERVAR]"), r.stdout.index("[ATRIBUIR]"))

    def test_versao(self):
        self.assertIn("Tropeiro", trem("versao").stdout)

    def test_trem_desconhecido(self):
        self.assertEqual(trem("naoexiste").returncode, 2)

    def test_planejada_nao_quebra(self):
        r = trem("rastro")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("planejada", r.stdout + r.stderr)

    def test_roda_tool_empacotada(self):
        r = trem("placar", str(CENARIO), str(DEMO))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Vencedor:** azul", r.stdout)

    def test_layout_instalado(self):
        """Simula a pasta /opt/tocaia do container e da ISO."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            shutil.copytree(RAIZ / "dist", base / "dist")
            shutil.copy(RAIZ / "catalogo.json", base)
            r = trem("silencio", str(DEMO), base=base)
            self.assertEqual(r.returncode, 1, r.stderr)  # 1 = achou silêncio
            self.assertIn("SILÊNCIO", r.stdout)


class TestPlacar(unittest.TestCase):
    def setUp(self):
        self.cenario = json.loads(CENARIO.read_text(encoding="utf-8"))
        self.alertas = placar.ler_alertas(DEMO)

    def test_resultado_da_demo(self):
        r = placar.jogar(self.cenario, self.alertas)
        self.assertEqual(r["vencedor"], "azul")
        self.assertEqual(r["lacunas"], ["T1053.005", "T1135"])
        self.assertEqual(r["cobertura_pct"], 66.7)

    def test_deteccao_pela_ausencia(self):
        r = placar.jogar(self.cenario, self.alertas)
        p6 = next(p for p in r["passos"] if p["id"] == "P6")
        self.assertTrue(p6["detectado"])
        self.assertIn("ausência", p6["como"])

    def test_host_errado_nao_conta(self):
        passo = dict(self.cenario["passos"][0], alvo="outro-host")
        r = placar.julgar_passo(passo, self.alertas, 600, True)
        self.assertFalse(r["detectado"])

    def test_regra_explicita(self):
        passo = dict(self.cenario["passos"][2], regras=["100900"])  # heartbeat vale como regra
        self.assertTrue(placar.julgar_passo(passo, self.alertas, 600, True)["detectado"])

    def test_tecnica_pai(self):
        self.assertTrue(placar.tecnica_bate("T1059.003", ["T1059.001"], True))
        self.assertFalse(placar.tecnica_bate("T1059.003", ["T1059.001"], False))

    def test_relatorio_markdown(self):
        md = placar.em_markdown(placar.jogar(self.cenario, self.alertas))
        self.assertIn("| P6", md)
        self.assertIn("Lacunas", md)


class TestSilencio(unittest.TestCase):
    def test_acha_host_calado(self):
        with open(DEMO, encoding="utf-8") as f:
            r = silencio.analisar(silencio.ler_eventos(f, "agent.name", "timestamp"))
        estados = {x["fonte"]: x["estado"] for x in r}
        self.assertEqual(estados["win-lab-01"], "SILÊNCIO")
        self.assertEqual(estados["linux-lab-01"], "normal")

    def test_fuso_sem_dois_pontos(self):
        d = silencio.para_data("2026-10-12T14:00:00.000-0300")
        self.assertEqual(d.utcoffset().total_seconds(), -3 * 3600)

    def test_pouco_dado(self):
        linhas = [json.dumps({"h": "a", "t": 1000 + i}) for i in range(3)]
        r = silencio.analisar(silencio.ler_eventos(linhas, "h", "t"))
        self.assertEqual(r[0]["estado"], "pouco dado")

    def test_linha_invalida_e_ignorada(self):
        buf = io.StringIO()
        sys_err, sys.stderr = sys.stderr, buf
        try:
            r = silencio.ler_eventos(["isso não é json", '{"h":"a","t":1}'], "h", "t")
        finally:
            sys.stderr = sys_err
        self.assertEqual(len(r["a"]), 1)


class TestManifesto(unittest.TestCase):
    def test_id_estavel_e_verificacao(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            shutil.copytree(RAIZ / "dist", base / "dist")
            m1, m2 = manifesto.montar(base), manifesto.montar(base)
            self.assertEqual(m1["id"], m2["id"])
            salvo = base / "m.json"
            salvo.write_text(json.dumps(m1), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(manifesto.verificar(salvo, m1), 0)
                (base / "dist" / "opsec.pyz").write_bytes(b"adulterado")
                self.assertEqual(manifesto.verificar(salvo, manifesto.montar(base)), 1)


class TestOpsec(unittest.TestCase):
    def test_checagem_local(self):
        r = opsec.checar()
        for chave in ("fuso", "idioma", "maquina", "checklist", "alertas"):
            self.assertIn(chave, r)
        self.assertGreaterEqual(len(r["checklist"]), 5)


class TestIso(unittest.TestCase):
    def test_menu_por_fases(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            menu.gerar(CATALOGO, raiz)
            atalhos = list((raiz / "usr/share/applications").glob("tocaia-*.desktop"))
            self.assertEqual(len(atalhos), len(CATALOGO))
            arvore = ET.parse(raiz / "etc/xdg/menus/applications-merged/tocaia.menu")
            nomes = [n.text for n in arvore.iter("Menuname")]
            self.assertEqual(nomes[0], "TOCAIA-Tracar")
            self.assertEqual(len(nomes), 6)

    def test_fase_invalida(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                menu.gerar({"x": {"fase": "Inventada", "desc": "?"}}, Path(tmp))

    def test_tema_gerado(self):
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(io.StringIO()):
                tema.main(tmp)
            svg = Path(tmp) / "usr/share/backgrounds/tocaia/tocaia.svg"
            ET.parse(svg)  # SVG válido
            css = (Path(tmp) / "etc/skel/.config/gtk-3.0/gtk.css").read_text(encoding="utf-8")
            self.assertIn(tema.P["menta"], css)

    def test_hooks_e_scripts_existem(self):
        for rel in ("iso/auto/config", "iso/construir-iso.sh",
                    "iso/config/hooks/normal/9000-tocaia.hook.chroot",
                    "iso/config/package-lists/tocaia.list.chroot"):
            self.assertTrue((RAIZ / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()

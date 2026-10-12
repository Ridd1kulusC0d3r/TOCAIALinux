"""Testes do núcleo da TOCAIA — só unittest da stdlib.

Rode da raiz do repositório:
    python3 -m unittest discover -s testes -v
"""
import importlib.util
import json
import os
import random
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.environ["TOCAIA_HOME"] = str(RAIZ)
os.environ["TOCAIA_ETICA"] = "aceito"
os.environ["TOCAIA_DADOS"] = tempfile.mkdtemp(prefix="tocaia-teste-")


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


trem = carregar("trem", RAIZ / "trem" / "trem.py")
relogio = carregar("relogio", RAIZ / "ferramentas" / "relogio" / "__main__.py")


class TestCatalogo(unittest.TestCase):
    def test_catalogo_valido(self):
        cat = trem.carregar_catalogo()
        self.assertEqual(len(cat["fases"]), 6, "TOCAIA tem seis fases")

    def test_letras_formam_tocaia(self):
        cat = trem.carregar_catalogo()
        self.assertEqual("".join(f["letra"] for f in cat["fases"].values()), "TOCAIA")

    def test_toda_fase_tem_ferramenta_pronta(self):
        cat = trem.carregar_catalogo()
        fases_com_pronta = {t["fase"] for t in cat["ferramentas"].values() if t["status"] == "pronta"}
        self.assertEqual(fases_com_pronta, set(cat["fases"]))

    def test_validador_pega_erro(self):
        ruim = {"fases": {"tracar": {}}, "ferramentas": {"X y": {"fase": "nada", "tipo": "?"}}}
        with self.assertRaises(ValueError):
            trem.validar_catalogo(ruim)

    def test_pronta_exige_campos_do_tipo(self):
        ruim = {"fases": {"tracar": {}}, "ferramentas": {"x": {
            "fase": "tracar", "tipo": "pip", "desc": "d", "status": "pronta", "origem": "terceiro"}}}
        with self.assertRaises(ValueError):
            trem.validar_catalogo(ruim)


class TestMenuEManifesto(unittest.TestCase):
    def test_menu_gera_um_desktop_por_ferramenta_pronta(self):
        cat = trem.carregar_catalogo()
        prontas = sum(1 for t in cat["ferramentas"].values() if t["status"] == "pronta")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(trem.gerar_menu(d), prontas)
            texto = (Path(d) / "tocaia-relogio.desktop").read_text(encoding="utf-8")
            self.assertIn("Categories=X-TOCAIA-Tracar;", texto)

    def test_manifesto_detecta_adulteracao(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "m.json"
            trem.manifesto(str(arq))
            integro, mesmo = trem.verificar_manifesto(arq)
            self.assertTrue(integro)
            self.assertTrue(mesmo)
            doc = json.loads(arq.read_text(encoding="utf-8"))
            doc["ambiente"]["python"] = "0.0.0"
            arq.write_text(json.dumps(doc), encoding="utf-8")
            integro, _ = trem.verificar_manifesto(arq)
            self.assertFalse(integro)

    def test_manifesto_tem_hash_do_relogio(self):
        doc = trem._corpo_manifesto()
        self.assertEqual(len(doc["ferramentas"]["relogio"]["sha256"]), 64)


class TestRelogio(unittest.TestCase):
    def setUp(self):
        self.csv = RAIZ / "casos" / "demo-bx7" / "postagens.csv"
        self.horarios, _ = relogio.ler_horarios(self.csv)
        self.r = relogio.analisar(self.horarios)

    def test_caso_bx7_fuso(self):
        self.assertEqual(self.r["fuso_inferido"]["fuso"], "UTC-03:00")

    def test_caso_bx7_silencio(self):
        self.assertEqual(len(self.r["silencios"]), 1)
        s = self.r["silencios"][0]
        self.assertEqual(s["dias"], 7)
        self.assertEqual(s["dia_zero"], "2026-09-02")

    def test_caso_bx7_pico(self):
        self.assertEqual(len(self.r["picos"]), 1)
        self.assertEqual(self.r["picos"][0]["inicio"], "2026-08-25")

    def test_todo_achado_tem_refutacao(self):
        for a in self.r["achados"]:
            self.assertIn(a["confianca"], "AMB")
            self.assertTrue(a["derrubaria"])

    def test_bot_de_relogio(self):
        inicio = datetime(2026, 1, 1, tzinfo=timezone.utc)
        bot = [inicio + timedelta(hours=3 * i) for i in range(60)]  # sempre no minuto :00
        r = relogio.analisar(bot)
        self.assertTrue(r["automacao"]["suspeito"])

    def test_humano_nao_e_bot(self):
        rng = random.Random(1)
        inicio = datetime(2026, 1, 1, tzinfo=timezone.utc)
        humano = sorted(inicio + timedelta(minutes=rng.randint(0, 60 * 24 * 30)) for _ in range(150))
        self.assertFalse(relogio.analisar(humano)["automacao"]["suspeito"])

    def test_html_tem_cadeia_de_custodia(self):
        pagina = relogio.gerar_html(self.r, self.csv, relogio.sha256_arquivo(self.csv))
        self.assertIn(relogio.sha256_arquivo(self.csv), pagina)
        self.assertIn("<svg", pagina)

    def test_epoch_e_sem_fuso(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("timestamp\n1767225600\n2026-01-01T10:00:00\nlixo\n")
        horarios, avisos = relogio.ler_horarios(f.name)
        os.unlink(f.name)
        self.assertEqual(len(horarios), 2)
        self.assertTrue(any("sem fuso" in a for a in avisos))
        self.assertTrue(any("ilegível" in a for a in avisos))


class TestTema(unittest.TestCase):
    def test_gerador_de_tema(self):
        gerar = carregar("gerar_tema", RAIZ / "tema" / "gerar_tema.py")
        with tempfile.TemporaryDirectory() as d:
            gerar.gerar(Path(d))
            base = Path(d) / "usr" / "share" / "themes" / "TOCAIA"
            self.assertTrue((base / "gtk-3.0" / "gtk.css").exists())
            self.assertTrue((base / "xfwm4" / "themerc").exists())
            png = (base / "xfwm4" / "close-active.png").read_bytes()
            self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
            self.assertTrue((Path(d) / "usr" / "share" / "tocaia" / "wallpaper.svg").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

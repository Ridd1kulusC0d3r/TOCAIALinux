# TOCAIA OSINT Linux — 1.0 "Tropeiro"

Distro de OSINT leve e universal, com o menu organizado pelas **fases do método TOCAIA** (Traçar, Observar, Cercar, Aguardar, Interpretar, Atribuir) em vez de por tipo de ferramenta. Parte do ecossistema **DEIVOSINT**.

> Fonte aberta, sem invadir, sem enganar, sem assediar. A distro serve para investigação ética e defesa.

## Uma receita, seis formas de usar

| Variante | Base | Tamanho | Onde roda | Como |
|---|---|---|---|---|
| **ISO live** (pendrive) | Debian 13 + Xfce com tema TOCAIA | centenas de MB | qualquer PC | `sudo sh iso/construir-iso.sh` ou baixe do Release |
| **Container** | Alpine | dezenas de MB | Linux, Mac, Windows, nuvem, Raspberry | `docker run -it ghcr.io/ridd1kulusc0d3r/tocaialinux` |
| **WSL** | Alpine | dezenas de MB | Windows sem VM | `sh container/exportar-wsl.sh` + `wsl --import` |
| **Codespaces** | Debian (devcontainer) | — | navegador | botão "Code → Codespaces" no GitHub |
| **Colab** | Ubuntu do Google | — | navegador | `nuvem/TOCAIA_Colab.ipynb` |
| **Celular "Matula"** | Debian 13 + Xfce no Termux (proot ou chroot) | ~1,5 GB | Android 10+ ARM64; tela no celular, PC ou TV | [COMECE-AQUI-CELULAR.md](COMECE-AQUI-CELULAR.md) |

## Em 60 segundos (só precisa de Python 3.10+)

```bash
git clone https://github.com/Ridd1kulusC0d3r/TOCAIALinux.git && cd TOCAIALinux
python3 build.py                 # empacota as tools em dist/*.pyz
python3 trem/trem.py             # lista os trens por fase
python3 trem/trem.py placar wargames/cenarios/rodada1-tropeiro-x-atalaia.json wargames/demo/alerts-demo.json
```

Ou dê dois cliques em `iniciar.sh` (Linux), `iniciar.command` (Mac) ou `iniciar.bat` (Windows).

## O `trem`

Em Minas tudo é trem. O lançador é um arquivo só, stdlib pura:

```
trem                lista por fase
trem fases          explica as 6 fases
trem <tool> [args]  roda; tools de terceiros instalam sozinhas na 1ª vez, num venv isolado
```

## Trens desta versão

| Trem | Fase | O que faz |
|---|---|---|
| `opsec` | Observar | checagem local do ambiente + checklist de OPSEC |
| `silencio` | Aguardar | **detecção pela ausência**: fontes (hosts, perfis, feeds) que calaram |
| `placar` | Interpretar | juiz do **war game ataque × defesa** sobre o Wazuh |
| `manifesto` | Atribuir | **cadeia de custódia do ferramental**: hash de cada tool usada |
| `maigret`, `holehe`, `sherlock` | Cercar | terceiros, sob demanda |

RASTRO, SÓSIA, PRISMA, VINCULA, F.I.O. e PASSEltr estão no catálogo como `planejada`. Veja [docs/PROJETOS.md](docs/PROJETOS.md).

## Estrutura

```
trem/trem.py          lançador
catalogo.json         todas as tools, com fase e tipo (pyz | pip | planejada)
tools/<nome>/         código de cada tool própria (vira dist/<nome>.pyz)
container/            Dockerfile Alpine, exportador WSL, saudação do shell
iso/                  live-build (Debian trixie), hook, pacotes, gerador do menu por fases
tema/                 paleta.json + gerador de GTK, terminal, login e wallpaper
wargames/             cenários, demo sintética, scripts do laboratório Wazuh
nuvem/                notebook do Colab
celular/              edição Android "Matula": modo DeX com Termux:X11, scrcpy e Miracast
.devcontainer/        Codespaces
testes/               25 testes, stdlib
docs/                 manual ilustrado (manual.html), projetos, relatório de testes
```

## Documentação

- **[COMECE-AQUI.md](COMECE-AQUI.md)** — o primeiro passo, sem jargão
- **[docs/manual.html](docs/manual.html)** — manual ilustrado (abra no navegador)
- **[COMECE-AQUI-CELULAR.md](COMECE-AQUI-CELULAR.md)**, **[docs/CELULAR.md](docs/CELULAR.md)** e **[docs/manual-celular.html](docs/manual-celular.html)** — a TOCAIA no Android
- **[wargames/README.md](wargames/README.md)** — regras do war game
- **[docs/RELATORIO-TESTES.md](docs/RELATORIO-TESTES.md)** — o que foi testado e onde

## Licença

Código sob MIT ([LICENSE](LICENSE)). Tools de terceiros não são redistribuídas: o catálogo só aponta para elas, e cada uma mantém a própria licença.

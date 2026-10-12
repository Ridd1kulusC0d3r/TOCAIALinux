<div align="center">

# ◆ TOCAIA OSINT Linux

**A doutrina virou sistema.** Uma distribuição Linux de OSINT, leve e com identidade própria,
organizada pelas **fases da investigação** — não por tipo de ferramenta.

`1.0 "Tropeiro"` · DEIVOSINT · OSINT no Jutsu

**leia o padrão · ouça o silêncio · posicione-se e espere**

</div>

---

## Por que ela existe

Kali, Parrot e afins organizam o menu por tipo de ferramenta ("Information Gathering",
"Web"...). A TOCAIA organiza pelo **método**: Traçar · Observar · Cercar · Aguardar ·
Interpretar · Atribuir. Navegar no menu já ensina a investigar. É mais leve que Kali e
Parrot, nasce em português, e traz **cadeia de custódia do ferramental** embutida.

## Quatro jeitos de rodar

| Edição | Para quê | Peso | Precisa |
|---|---|---|---|
| ☁️ **Colab** | testar sem instalar | zero | navegador — [`nuvem/colab`](nuvem/colab/) |
| ☁️ **Codespaces** | mexer no código | zero | GitHub — [`.devcontainer`](.devcontainer/) |
| 🐳 **Container / WSL** | uso diário, leve | dezenas de MB | Docker/WSL — [`edicoes/alpine`](edicoes/alpine/) |
| 💿 **ISO Debian + Xfce** | a distro completa | ~1–1,5 GB | pendrive/VM — [`edicoes/debian`](edicoes/debian/) |

> **Comece por [`COMECE-AQUI.md`](COMECE-AQUI.md)** e pelo **Manual Ilustrado**
> ([`docs/manual/index.html`](docs/manual/index.html) — abra no navegador).

## O comando `trem`

Em Minas, tudo é trem. Aqui, cada ferramenta também:

```
trem                 # lista as ferramentas, agrupadas pelas 6 fases
trem fases           # a doutrina
trem relogio --demo  # roda a ferramenta RELÓGIO no caso de exemplo
trem etica           # as regras de engajamento (leia antes de investigar)
trem manifesto       # cadeia de custódia do seu ferramental (cite no laudo)
trem doutor          # checagem de saúde
```

Ferramentas de terceiro (Sherlock, Maigret, Holehe...) **não** vêm instaladas: o `trem`
instala cada uma, isolada, só na primeira vez. A base continua leve.

## O que já vem pronto

- **`trem`** — lançador stdlib, catálogo por fase, menu gráfico, `doutor`, ética.
- **RELÓGIO** — ferramenta própria (fase Traçar): lê horários de postagens públicas e
  revela padrão de vida, fuso, picos e **silêncios**, com relatório HTML e cadeia de custódia.
- **Tema TOCAIA** — GTK, janelas (xfwm4), terminal, wallpaper e login gerados de um arquivo
  só (`tema/tokens.json`), com a arte da onça na espreita e a face de olhos ciano.
- **Manifesto** — SHA-256 de cada ferramenta + versões, com ID reproduzível para o laudo.
- **Catálogo de terceiros** — Sherlock, Maigret, Holehe, socialscan, exiftool, mat2, whois, dig...

## Estrutura

```
trem/            o lançador            tema/        gerador do visual (tokens → tudo)
catalogo/        a fonte da verdade    assets/      artes da marca + gerador
ferramentas/     ferramentas próprias  edicoes/     debian (ISO) e alpine (container)
casos/           caso de demonstração  nuvem/       Colab   ·  .devcontainer/ Codespaces
docs/            manual + guias + PROJETOS.md + EVOLUCAO.md
testes/          python3 -m unittest discover -s testes
```

## Em quais dos seus projetos dá para entrar

A classificação completa das suas ferramentas por fase e por prontidão de integração
está em **[`docs/PROJETOS.md`](docs/PROJETOS.md)**. O roteiro de evolução (e o esqueleto
da próxima ferramenta) está em **[`docs/EVOLUCAO.md`](docs/EVOLUCAO.md)**.

## Desenvolvimento

```
python3 -m unittest discover -s testes -v     # testes (ver RELATORIO-DE-TESTES.md)
bash scripts/empacotar.sh                      # empacota as ferramentas em .pyz
python3 tema/gerar_tema.py --destino ./saida   # gera o tema para inspecionar
sudo edicoes/debian/build.sh                   # constrói a ISO (precisa de live-build)
edicoes/alpine/build.sh --wsl                  # constrói o container e exporta p/ WSL
```

## Ética

Fonte pública · zero interação · base legal (LGPD · Marco Civil). Perfil é hipótese, não
sentença (rotule A/M/B). **Ler não é invadir. Esperar não é emboscar.**

## Licença

MIT (código próprio). Ferramentas de terceiro mantêm suas licenças; a TOCAIA distribui
o catálogo, não o código delas (modelo sob demanda). Créditos no manual.

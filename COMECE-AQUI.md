# ◆ COMECE AQUI — TOCAIA OSINT Linux 1.0 "Tropeiro"

> **leia o padrão · ouça o silêncio · posicione-se e espere**

Você tem em mãos uma distribuição Linux inteira, sua, com a doutrina TOCAIA virada
sistema operacional. Este arquivo é o mapa. Leva 5 minutos.

Como você vai **aprender os dois sistemas novos** (Debian com interface e Alpine no
terminal), a documentação é o coração do projeto — e está toda em português, do zero.

---

## 1. Escolha por onde começar

Há **quatro jeitos** de rodar a TOCAIA. Comece pelo mais fácil para o seu momento:

| Jeito | Para quê | Peso | Precisa de |
|---|---|---|---|
| ☁️ **Colab** | testar sem instalar nada, estudar as ferramentas | zero | só o navegador |
| ☁️ **Codespaces** | mexer no código da distro no navegador | zero | conta GitHub |
| 🐳 **Container/WSL (Alpine)** | usar no dia a dia, no terminal, leve | dezenas de MB | Docker ou WSL |
| 💿 **ISO (Debian + Xfce)** | a distro completa, bonita, com interface | ~1–1,5 GB | pendrive ou VM |

**Abra no Colab agora (sem instalar nada):**
- ☁️ Otimizado (terminal + relatórios): https://colab.research.google.com/github/Ridd1kulusC0d3r/TOCAIALinux/blob/main/nuvem/colab/TOCAIA_OSINT_Linux.ipynb
- 🖥️ Desktop (ver a cara do sistema): https://colab.research.google.com/github/Ridd1kulusC0d3r/TOCAIALinux/blob/main/nuvem/colab/TOCAIA_Colab_Desktop.ipynb

**Sugestão de rota de aprendizado:**
1. Abra o **Colab** hoje (`nuvem/colab/TOCAIA_OSINT_Linux.ipynb`) — sinta o `trem` e o RELÓGIO.
2. Depois rode o **container Alpine** — é o Linux de terminal, universal. Aqui você aprende o essencial sem medo de quebrar nada.
3. Por fim, grave a **ISO Debian** num pendrive (modo live, sem instalar) — a experiência completa com interface gráfica.

O **Manual Ilustrado** (`docs/manual/index.html` — abra no navegador) tem o passo a
passo de instalação de cada um, com telas anotadas e diagramas.

---

## 2. O comando que você mais vai usar: `trem`

Em Minas, tudo é trem. Aqui também:

```
trem                 # lista as ferramentas, agrupadas pelas 6 fases da TOCAIA
trem fases           # explica as fases: Traçar Observar Cercar Aguardar Interpretar Atribuir
trem relogio --demo  # roda a ferramenta RELÓGIO no caso de demonstração
trem info relogio    # ficha de uma ferramenta
trem etica           # as regras de engajamento (leia antes de investigar)
trem manifesto       # cadeia de custódia do seu ferramental (para citar no relatório)
trem doutor          # checa se está tudo saudável
```

Ferramentas de terceiro (Sherlock, Maigret...) **não** vêm instaladas: o `trem`
instala cada uma, isolada, só na primeira vez que você usa. A base continua leve.

---

## 3. O que tem dentro do repositório

```
TOCAIALinux/
├── COMECE-AQUI.md          ← você está aqui
├── trem/trem.py            ← o lançador (stdlib pura)
├── catalogo/catalogo.json  ← a fonte da verdade: as ferramentas e suas fases
├── ferramentas/
│   └── relogio/            ← RELÓGIO (ferramenta própria, vira relogio.pyz)
├── casos/demo-bx7/         ← caso sintético de demonstração (#BX-7)
├── tema/                   ← gerador do visual (paleta do deck → GTK, janelas, wallpaper)
├── edicoes/
│   ├── debian/             ← ISO com Xfce (live-build)
│   └── alpine/             ← container/WSL (Dockerfile)
├── nuvem/colab/            ← notebook do Colab
├── .devcontainer/          ← Codespaces
├── docs/                   ← o coração: manual, guias e classificação dos projetos
│   ├── manual/index.html   ← MANUAL ILUSTRADO (abra no navegador)
│   ├── GUIA-DEBIAN.md       ← aprendendo o sistema com interface
│   ├── GUIA-ALPINE.md       ← aprendendo o sistema de terminal
│   ├── PROJETOS.md          ← em quais dos SEUS projetos você pode entrar, por fase
│   └── EVOLUCAO.md          ← próximos passos e esqueleto da próxima ferramenta
├── testes/                 ← testes (python3 -m unittest discover -s testes)
└── RELATORIO-DE-TESTES.md  ← resultado dos testes rodados na nuvem
```

---

## 4. As 6 fases (a doutrina virada menu)

O menu gráfico da TOCAIA **não** é organizado por tipo de ferramenta, como no Kali ou
Parrot. É organizado pelas fases do método. Navegar no menu já ensina a investigar:

1. **T · Traçar** — trace o padrão de vida (ritmo, horários, círculos).
2. **O · Observar** — observe sem nunca tocar (coleta passiva + OPSEC).
3. **C · Cercar** — cerque o nó inescapável (pivotagem, grafo de vínculos).
4. **A · Aguardar** — aguarde no ponto inevitável (vigília, tripwires).
5. **I · Interpretar** — interprete o vazio (linha de base, desvio, silêncio).
6. **A · Atribuir** — atribua com confiança (grau A/M/B, cadeia de custódia, base legal).

---

## 5. Antes de tudo: a ética

A TOCAIA é um método de espreita em **fontes públicas**. A regra é simples e inegociável:

- **fonte pública**, sem burlar barreira;
- **zero interação** com o alvo — curtir, seguir ou contatar **destrói a tocaia**;
- **base legal** (LGPD · Marco Civil) e finalidade legítima;
- **perfil é hipótese, não sentença** — rotule a confiança (A/M/B).

> Ler não é invadir. Esperar não é emboscar.

Rode `trem etica` sempre que precisar relembrar.

---

**DEIVOSINT · OSINT no Jutsu** · Próximo passo: abra `docs/manual/index.html`.

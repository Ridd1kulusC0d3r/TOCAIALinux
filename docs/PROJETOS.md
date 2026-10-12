# Em quais projetos você pode entrar — mapa das suas ferramentas nas fases da TOCAIA

A TOCAIA Linux não começa vazia: ela é a casa natural das ferramentas que você já
vem criando. Este documento classifica cada projeto seu por **fase da doutrina** e
por **prontidão de integração**, para você saber onde cada um encaixa e qual é o
menor passo para colocá-lo dentro da distro.

## Como a integração funciona (relembrando)

Cada ferramenta é uma linha no `catalogo/catalogo.json`. O `trem`, o menu gráfico, o
manifesto e a documentação leem desse catálogo. Integrar um projeto é, no fundo,
**adicionar uma linha** e apontar como ele roda:

| `tipo` | quando usar | o que precisa |
|---|---|---|
| `pyz`  | ferramenta sua, stdlib, de arquivo único | pasta com `__main__.py` → vira `.pyz` |
| `git`  | repo seu/terceiro que roda por um script | `repo` + `entrada` (script principal) |
| `pip`  | pacote publicado no PyPI | `pip` + `comando` |
| `sistema` | binário do sistema | `comando` + `apt`/`apk` |
| `web`  | serviço que abre no navegador | `url` |

Prontidão:
- **🟢 pronta** — já no catálogo e rodando (ou a um `.pyz` de distância).
- **🟡 1 passo** — falta só definir o ponto de entrada (script principal) ou publicar o repo.
- **🔵 planejada** — no forno; precisa de empacotamento/adaptação antes de entrar.

---

## T · Traçar — padrão de vida

| Projeto | Prontidão | Menor passo para entrar |
|---|---|---|
| **RELÓGIO** (nova, criada aqui) | 🟢 pronta | já é a ferramenta-vitrine da fase |
| **F.I.O. Lab** (telefones, registros BR) | 🔵 planejada | expõe um `fio.py` como entrada; `tipo: git` |

## O · Observar — coleta passiva e OPSEC

| Projeto | Prontidão | Menor passo |
|---|---|---|
| **PASSEltr** (coleta passiva + cadeia de custódia) | 🔵 planejada | definir `entrada` e publicar; casa com o manifesto da TOCAIA |
| **ética** (regras de engajamento) | 🟢 pronta | embutida no `trem etica` |

## C · Cercar — pivotagem e grafo de vínculos

| Projeto | Prontidão | Menor passo |
|---|---|---|
| **DEIVOSINT PRISMA** (runner unificado stdlib) | 🟡 1 passo | é o candidato mais forte: já é stdlib e unificado; só falta `entrada` |
| **VINCULA** (vínculos por reportagem/celular) | 🟡 1 passo | repo público existe (`Ridd1kulusC0d3r/VINCULA`); definir script principal |
| **OsintbrFLOW** (fork BR do Flowsint) | 🔵 planejada | empacotar como `git`; já tem notebook Colab |
| **sherlock / maigret / holehe / socialscan** (terceiros) | 🟢 pronta | já no catálogo, sob demanda |

## A · Aguardar — vigília e tripwires

| Projeto | Prontidão | Menor passo |
|---|---|---|
| **VIGIA** (nova; vigília de páginas/feeds) | 🔵 planejada | próxima ferramenta stdlib sua (urllib + hashlib) — esqueleto sugerido abaixo |
| **SÓSIA** (radar de perfis imitadores) | 🔵 planejada | empacotar `__main__.py`; vira `pyz` |
| **Canarytokens** (terceiro, defensivo) | 🟢 pronta | `web`, já no catálogo |

## I · Interpretar — ausência, desvio, arquivo

| Projeto | Prontidão | Menor passo |
|---|---|---|
| **RASTRO** (arqueologia de username via Wayback) | 🔵 planejada | empacotar `__main__.py`; irmã do SÓSIA |
| **Detecção pela Ausência** (sua tese) | 🔵 conceito | o motor de silêncios do RELÓGIO já é um primeiro módulo aplicável |
| **waybackpy** (terceiro) | 🟢 pronta | já no catálogo |

## A · Atribuir — conclusão com confiança

| Projeto | Prontidão | Menor passo |
|---|---|---|
| **manifesto** (cadeia de custódia do ferramental) | 🟢 pronta | embutido no `trem manifesto` |
| **DVV — Documentação Viva e Verificável** | 🟡 1 passo | o manifesto é a semente; estender para relatórios assinados |
| **TIEM/AXIS** (modelagem de ameaças) | 🔵 adjacente | não é coleta; entra como material/skill, não como ferramenta de fase |

---

## Projetos que NÃO entram como ferramenta de fase (e por quê)

Nem tudo é ferramenta de coleta. Estes são seus, valiosos, mas pertencem a outra
camada — entram na TOCAIA como **conteúdo, skill ou material de estudo**, não como
item do menu de investigação:

- **OSINT no Jutsu**, **Python para OSINT**, **Linux para OSINT**, **Investigador Cyber 90 dias** → trilhas de ensino. Podem virar o diretório `/usr/share/tocaia/trilhas` e um item "Aprender" no menu.
- **ALVORADA**, **Pensieve Intelligence**, **LLmInjection** → inteligência/boletins (produto contínuo, não ferramenta local).
- **Aurora SOC Lab**, **D&R Fighters** → treinamento/jogo (outro público).
- **MOSAIV**, **NIFA/NISC**, **MSL**, **Tratado cap. 26** → pesquisa acadêmica.
- **Nexus OSINT / OSINTList** → catálogos de links (viram um item `web` + uma skill de busca).
- **FraudNeuron / TRAMA** → fraud intelligence (domínio próprio; pode ganhar uma fase-extra "pagamentos" no futuro).

> Regra prática: **se coleta, observa ou cruza dado de uma investigação, é ferramenta de fase.**
> Se ensina, divulga ou pesquisa sobre o método, é material — entra noutra prateleira.

---

## Ordem de integração sugerida (menor esforço, maior ganho)

1. **DEIVOSINT PRISMA** → fase Cercar. É o maior salto: já é stdlib e unificado. Definir `entrada`, empacotar, pronto.
2. **VINCULA** → Cercar. Repo público já existe; só o script principal.
3. **RASTRO** e **SÓSIA** → Interpretar e Aguardar. Empacotar como `.pyz` (já são stdlib).
4. **VIGIA** → Aguardar. Criar do zero, pequena (veja o esqueleto sugerido em `docs/EVOLUCAO.md`).
5. **PASSEltr** → Observar. Casa com o manifesto; vira a ferramenta-âncora da fase.

Cada um desses é "adicione uma linha no catálogo + aponte a entrada". O `trem doutor`
e o CI avisam se algo ficou inconsistente.

# Onde cada projeto entra na TOCAIA OSINT Linux

Classificação dos projetos existentes do ecossistema DEIVOSINT/TOCAIA. A coluna **Como entra** diz o tipo no `catalogo.json`.

## 1. Tools no menu (viram "trens")

| Projeto | Fase | Como entra | Variante | Status |
|---|---|---|---|---|
| opsec | Observar | `pyz` embutida | todas | ✅ pronta |
| silencio | Aguardar | `pyz` embutida | todas | ✅ pronta |
| placar (war game) | Interpretar | `pyz` embutida | todas | ✅ pronta |
| manifesto | Atribuir | `pyz` embutida | todas | ✅ pronta |
| RASTRO | Cercar | `pyz` (stdlib) | todas | 🟡 empacotar em `tools/rastro/` |
| SÓSIA | Aguardar | `pyz` (stdlib) | todas | 🟡 empacotar em `tools/sosia/` |
| PRISMA | Interpretar | `pyz` (stdlib) | todas | 🟡 empacotar |
| VINCULA | Interpretar | `pyz` | todas | 🟡 empacotar |
| F.I.O. Lab 2.1 | Cercar | `pyz` + manual | ISO e Codespaces | 🟡 empacotar |
| PASSEltr | Atribuir | `pyz` (stdlib, cadeia de custódia) | todas | 🟡 empacotar |
| espectro_bolso / deteccao_por_ambiente (T.O.C.A.I.A.) | Aguardar / Observar | `pyz` | todas | 🟡 empacotar |
| OsintbrFLOW (fork do Flowsint) | Interpretar | sob demanda via Docker | só ISO desktop | 🔵 depois da 1.0 (pesado) |
| Maigret, Holehe, Sherlock | Cercar | `pip` sob demanda | todas | ✅ no catálogo |

**Regra para empacotar uma tool sua:** pasta `tools/<nome>/` com `__main__.py` que aceita `--help`; troque o tipo no catálogo de `planejada` para `pyz`; rode `python3 build.py` e os testes.

## 2. Conteúdo de estudo que vem junto (pasta `/opt/tocaia/estudos`, a partir da 1.1)

| Projeto | Por que entra |
|---|---|
| OSINT no Jutsu (109 cartas) | trilha gamificada, ranks D→S casam com o menu por fases |
| Python para OSINT 21 dias (63 cartas) | aprende a escrever os próprios trens |
| Linux para OSINT 21 dias | aprende a usar a própria distro |
| Investigador cyber 90 dias | trilha longa |
| ATLAS-8 | guia OSINT/CTI em HTML, roda offline |
| Nexus OSINT / OSINTList | favoritos do Firefox da ISO, organizados por fase |

## 3. Versões gratuitas na nuvem

| Opção | Custo | Para quê |
|---|---|---|
| GitHub Codespaces (`.devcontainer/`) | cota gratuita mensal da conta GitHub | terminal completo com `trem`, sem instalar |
| Google Colab (`nuvem/TOCAIA_Colab.ipynb`) | grátis | demo, aulas, rodar placar com seu alerts.json |
| OSINT-Colab (ex-OSINTIA) | grátis | modelos de IA para OSINT, vira o "vagão IA" do Colab |
| Imagem no GHCR | grátis para repositório público | `docker run ghcr.io/ridd1kulusc0d3r/tocaialinux` |

## 4. War games e defesa (módulo `wargames/`)

| Projeto | Reaproveitamento |
|---|---|
| Aurora SOC Lab (casos N1/N2/N3) | cada caso vira um cenário do placar; o modo turma vira o ranking |
| D&R Fighters | skin gamificada do placar (clãs = times vermelho/azul) |
| Ciclo EDOA + detecção pela ausência | já implementado no `silencio` e nos passos `"deteccao": "ausencia"` |
| Pré-projeto ARENA (wargaming formal + Wazuh) | o placar é o "juiz" operacional; a camada de teoria dos jogos fica no repositório acadêmico, separado da marca TOCAIA |

## 5. Wazuh (repositórios próprios para o programa de Ambassadors)

| Repositório sugerido | Origem que já existe | Ordem |
|---|---|---|
| `wazuh-silencio` — detecção pela ausência por cadência de fonte, com regras e script stdlib | `tools/silencio` + ciclo EDOA | 1º |
| `wazuh-purple-arena` — este módulo de war games publicado à parte | `wargames/` + `tools/placar` | 2º |
| `wazuh-osint-feeds` — abuse.ch/ThreatFox/URLhaus virando listas CDB atualizadas, stdlib | guia de threat hunting Wazuh + OpenSearch | 3º |
| `wazuh-inventario` — recriação do Maarckz/Inventory com snapshots e diff por hash | chat "Como recriamos isso?" | 4º |
| `wazuh-auditoria-4688` — liga auditoria de processo + linha de comando no Windows | `audit_wazuh.py` | 5º |
| `wazuh-ptbr` — tutoriais e playbooks de hunting em português | guia de threat hunting | contínuo |

## 6. NÃO publicar

Material interno da Clavis (OTO AI Analyst, Caso Vivo, regras e casos de cliente, análises de pentest de cliente) fica fora de qualquer repositório público. Use só versões genéricas e dados sintéticos.

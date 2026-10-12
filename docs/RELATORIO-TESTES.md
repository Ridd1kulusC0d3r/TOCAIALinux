# Relatório de testes — TOCAIA 1.0 "Tropeiro"

Data: 12/10/2026 · Ambiente: nuvem Linux, Python 3.13.16

## Resultado

| Teste | Resultado |
|---|---|
| Suíte `python3 -m unittest discover -s testes` (25 testes) | ✅ 25/25 |
| Empacotamento `build.py` (4 tools) | ✅ manifesto 4 KB · opsec 4 KB · placar 8 KB · silencio 8 KB |
| Instalação sob demanda real: `trem sherlock --version` | ✅ venv criado, Sherlock v0.16.2 rodou |
| Lançador de dois cliques `iniciar.sh` | ✅ build + testes + demo + `placar.md` |
| Demo do war game | ✅ azul 101,5 × vermelho 25 · cobertura 66,7% · MTTD 67,5 s · P6 detectado pela ausência |
| `trem silencio` na demo | ✅ só `win-lab-01` marcado como SILÊNCIO (13× o ritmo normal) |
| Sintaxe `sh -n` de auto/config, construir-iso, hook, exportar-wsl, saudação | ✅ |
| Manual HTML renderizado (desktop 1200 px e celular 390 px) | ✅ sem erro de JS, sem rolagem horizontal, abas funcionando |

## O que cobre a suíte

- **Catálogo:** fases válidas, toda `pyz` tem código e build, toda `pip` tem pacote e comando.
- **trem:** lista na ordem das fases, versão, trem desconhecido (código 2), planejada não quebra, roda tool empacotada, e o layout instalado em `/opt/tocaia` (o mesmo do container e da ISO).
- **placar:** resultado da demo, detecção pela ausência, host errado não pontua, regra explícita, técnica pai, relatório Markdown.
- **silencio:** acha o host calado, fuso `-0300`, "pouco dado", linha inválida ignorada.
- **manifesto:** ID estável e `--verificar` acusa adulteração de um `.pyz`.
- **ISO:** menu com 6 fases na ordem certa (XML válido), fase inválida é recusada, tema gera SVG válido e CSS com a paleta.

## Não testado aqui (roda no GitHub Actions)

| Item | Motivo | Onde será testado |
|---|---|---|
| Imagem Docker Alpine | este ambiente não alcança o Docker Hub | `ci.yml`, a cada push |
| ISO Debian 13 + Xfce | este ambiente não alcança os espelhos do Debian | `release.yml`, ao criar tag `v*` ou rodar manualmente |
| Windows e macOS | ambiente Linux | matriz do `ci.yml` |
| Nomes dos pacotes da ISO em trixie | sem acesso ao repositório Debian | 1ª execução do `release.yml` |
| Visual do tema na tela real | precisa da ISO | depois do 1º boot; ajustar `tema/paleta.json` |

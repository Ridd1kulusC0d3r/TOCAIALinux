# Relatório de testes — TOCAIA OSINT Linux

Gerado automaticamente. Reproduza com:

```
python3 -m unittest discover -s testes -v
```

## Resumo da última execução na nuvem

| Campo | Valor |
|---|---|
| Resultado | ✅ **todos os testes passaram** |
| Total de testes | 17 |
| Duração | 0.260s |
| Python | 3.13.16 |
| Plataforma | Linux-6.18.44-fc-v114-x86_64-with-glibc2.39 |
| Quando (UTC) | 2026-10-12T15:01:20+00:00 |

## Casos

| Teste | Resultado |
|---|---|
| `test_catalogo_valido` | ✅ passou |
| `test_letras_formam_tocaia` | ✅ passou |
| `test_pronta_exige_campos_do_tipo` | ✅ passou |
| `test_toda_fase_tem_ferramenta_pronta` | ✅ passou |
| `test_validador_pega_erro` | ✅ passou |
| `test_manifesto_detecta_adulteracao` | ✅ passou |
| `test_manifesto_tem_hash_do_relogio` | ✅ passou |
| `test_menu_gera_um_desktop_por_ferramenta_pronta` | ✅ passou |
| `test_bot_de_relogio` | ✅ passou |
| `test_caso_bx7_fuso` | ✅ passou |
| `test_caso_bx7_pico` | ✅ passou |
| `test_caso_bx7_silencio` | ✅ passou |
| `test_epoch_e_sem_fuso` | ✅ passou |
| `test_html_tem_cadeia_de_custodia` | ✅ passou |
| `test_humano_nao_e_bot` | ✅ passou |
| `test_todo_achado_tem_refutacao` | ✅ passou |
| `test_gerador_de_tema` | ✅ passou |

## O que cada bloco cobre

- **TestCatalogo** — as iniciais das fases soletram TOCAIA; toda fase tem ao menos uma
  ferramenta pronta; o validador rejeita tipo/status/campo inválidos antes de qualquer build.
- **TestMenuEManifesto** — o menu gera um `.desktop` por ferramenta pronta, com a categoria
  da fase certa; o manifesto detecta adulteração (muda 1 byte → `--verificar` acusa) e
  carrega o SHA-256 do RELÓGIO.
- **TestRelogio** — no caso sintético #BX-7, reencontra fuso (-03:00), o pico de 6 dias e o
  silêncio de 7 dias; distingue bot de humano; todo achado traz uma refutação; lê epoch,
  ISO sem fuso e descarta linhas ilegíveis com aviso.
- **TestTema** — o gerador de tema produz GTK, PNGs de janela válidos (assinatura PNG + CRC)
  e o wallpaper.

## Ambientes validados além dos testes unitários

| Alvo | Como foi verificado | Situação |
|---|---|---|
| Núcleo `trem` (lista, fases, info, manifesto, doutor) | execução direta na nuvem | ✅ |
| Geração do tema (GTK/xfwm4/terminal/wallpaper/menu/login) | gerado e inspecionado; 61 PNGs com CRC válido | ✅ |
| Marca (wallpaper espreita/face, login, ícones da face, GRUB) | gerado e renderizado (Chromium headless) | ✅ |
| RELÓGIO (relatório HTML + JSON + cadeia de custódia) | rodado no caso #BX-7 | ✅ |
| Edição Alpine (lógica, hints de `apk`, entrypoint) | simulada (Docker Hub bloqueado nesta sessão) | ✅ lógica · build real no CI |
| ISO Debian (`live-build`) | scripts validados (`bash -n`); build real no CI | ⏳ CI |
| Container multi-arch e export WSL | Dockerfile validado; build real no CI | ⏳ CI |

> Observação: o ambiente desta sessão bloqueia Docker Hub e os repositórios Debian/Alpine
> por política de egresso. Por isso a ISO e as imagens de container são construídas no
> **GitHub Actions** (rede plena). A lógica de todas as edições foi validada aqui.

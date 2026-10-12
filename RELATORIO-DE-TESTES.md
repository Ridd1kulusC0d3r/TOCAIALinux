# Relatório de testes — TOCAIA OSINT Linux (unificado)

```
python3 -m unittest discover -s testes -v
```

## Última execução na nuvem

| Campo | Valor |
|---|---|
| Resultado | ✅ **todos passaram** |
| Total | 21 |
| Duração | 0.202s |
| Python | 3.13.16 |
| Plataforma | Linux-6.18.44-fc-v114-x86_64-with-glibc2.39 |
| Quando (UTC) | 2026-10-12T19:33:08+00:00 |

## Casos

| Teste | Resultado |
|---|---|
| `test_catalogo_valido` | ✅ |
| `test_letras_formam_tocaia` | ✅ |
| `test_pronta_exige_campos_do_tipo` | ✅ |
| `test_toda_fase_tem_ferramenta_pronta` | ✅ |
| `test_validador_pega_erro` | ✅ |
| `test_manifesto_detecta_adulteracao` | ✅ |
| `test_manifesto_tem_hash_do_relogio` | ✅ |
| `test_menu_gera_um_desktop_por_ferramenta_pronta` | ✅ |
| `test_bot_de_relogio` | ✅ |
| `test_caso_bx7_fuso` | ✅ |
| `test_caso_bx7_pico` | ✅ |
| `test_caso_bx7_silencio` | ✅ |
| `test_epoch_e_sem_fuso` | ✅ |
| `test_html_tem_cadeia_de_custodia` | ✅ |
| `test_humano_nao_e_bot` | ✅ |
| `test_todo_achado_tem_refutacao` | ✅ |
| `test_gerador_de_tema` | ✅ |
| `test_opsec_tem_checklist` | ✅ |
| `test_placar_azul_vence_na_demo` | ✅ |
| `test_placar_tecnica_pai` | ✅ |
| `test_silencio_acha_host_mudo` | ✅ |

## Cobertura por bloco

- **TestCatalogo / TestMenuEManifesto / TestRelogio / TestTema** — núcleo OSINT: catálogo,
  fases, menu, manifesto (cadeia de custódia), RELÓGIO (padrão de vida/silêncios) e tema.
- **TestWargames** — a frente de detecção vinda da outra versão: `silencio` (detecção pela
  ausência, T1070/T1562), `placar` (juiz do war game sobre o Wazuh, ATT&CK/MTTD) e `opsec`
  (checklist local). O placar na demo dá azul 101,5 × vermelho 25, com P6 detectado pela ausência.

## Ambientes validados

| Alvo | Verificação | Situação |
|---|---|---|
| Núcleo `trem` + ferramentas próprias | execução direta | ✅ |
| Tema + marca (onça/face, login, ícones) | gerado e renderizado | ✅ |
| Wargames (silencio/placar) na demo | rodado ponta a ponta | ✅ |
| Edição Alpine (container/WSL) arm64+amd64 | lógica validada; build no CI | ✅ / ⏳ CI |
| Edição Termux (Poco X6 Pro) | `bash -n` + lógica; roda no aparelho | ✅ lógica |
| Edição Raspberry Pi (baremetal arm64) | `bash -n` + lógica; roda no Pi | ✅ lógica |
| ISO Debian amd64/arm64 (live-build) | scripts validados; build no CI | ⏳ CI |

> Docker Hub e os repositórios Debian/Alpine são bloqueados por política de egresso nesta
> sessão; ISO e imagens de container são construídas no GitHub Actions (rede plena).

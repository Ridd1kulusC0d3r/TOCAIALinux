# Planos de evolução — para onde a TOCAIA Linux cresce

A distro foi desenhada para crescer **somando linhas ao catálogo**, não reescrevendo o
núcleo. Este documento guarda o roteiro e o esqueleto da próxima ferramenta.

## Roteiro por versão (codinomes mineiros)

| Versão | Codinome | Foco |
|---|---|---|
| 1.0 | **Tropeiro** | núcleo: `trem`, RELÓGIO, tema, ISO Debian, container Alpine, nuvem |
| 1.1 | **Pão de Queijo** | integrar PRISMA e VINCULA (fase Cercar); VIGIA (fase Aguardar) |
| 1.2 | **Torresmo** | RASTRO e SÓSIA empacotados; relatórios assinados (DVV) |
| 2.0 | **Cafezin** | variante "desktop" com navegador dedicado e perfis OPSEC |
| —   | Broa, Quitanda... | conforme as ferramentas amadurecem |

## Três degraus de entrega (o mesmo do OsintbrFLOW)

Cada ferramenta que entra deve caminhar nos três degraus:
1. **pacote** — roda pelo `trem` (`.pyz` ou `git`);
2. **dois cliques** — lançador para leigos;
3. **hospedado** — Colab/Codespaces para a equipe testar sem instalar.

## Inovação transversal já embutida: cadeia de custódia do ferramental

O `trem manifesto` gera um JSON com o SHA-256 de cada ferramenta e a versão de cada
pacote sob demanda, mais um ID que muda a qualquer alteração. Citar esse ID no
relatório deixa a coleta **reproduzível** — peso pericial, e a ponte natural para o
seu DVV e para o PASSEltr.

## Próxima ferramenta sugerida: VIGIA (fase Aguardar)

Pequena, stdlib, encaixa direto. Esqueleto para `ferramentas/vigia/__main__.py`:

```python
#!/usr/bin/env python3
"""VIGIA — aguarde no ponto inevitável. Avisa quando uma página pública muda."""
import hashlib, json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ESTADO = Path.home() / ".local/share/tocaia/vigia.json"

def impressao(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TOCAIA-VIGIA/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return hashlib.sha256(r.read()).hexdigest()

def vigiar(urls):
    antigo = json.loads(ESTADO.read_text()) if ESTADO.exists() else {}
    agora = datetime.now(timezone.utc).isoformat()
    novo = {}
    for url in urls:
        try:
            h = impressao(url)
        except Exception as e:                      # rede falha: registra, não quebra
            print(f"[!] {url}: {e}"); continue
        mudou = url in antigo and antigo[url]["hash"] != h
        marca = "MUDOU" if mudou else ("novo" if url not in antigo else "igual")
        print(f"[{marca}] {url}")
        novo[url] = {"hash": h, "visto": agora}
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(novo, indent=2))

if __name__ == "__main__":
    vigiar(sys.argv[1:] or ["https://example.org"])
```

Para integrar: empacotar (`scripts/empacotar.sh` já pega) e trocar o status de `vigia`
no catálogo de `planejada` para `pronta`, com `"tipo": "pyz", "arquivo": "vigia.pyz"`.
O `trem doutor` e o CI confirmam que ficou consistente.

## Ideias maiores (quando houver fôlego)

- **Fase-extra "Pagamentos"** para o FraudNeuron/TRAMA (fora do TOCAIA clássico).
- **Item "Aprender"** no menu, abrindo as trilhas (OSINT no Jutsu, Python/Linux para OSINT).
- **Persistência criptografada** no pendrive live (LUKS), para investigação em campo.
- **Assinatura do manifesto** com chave do analista (passo final do DVV).

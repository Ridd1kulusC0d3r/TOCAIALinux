# TOCAIA em ARM — celular, Raspberry Pi e containers

A TOCAIA roda em ARM64. O que muda é **quão "no metal"** cada alvo deixa chegar.

| Alvo | Como | Baremetal? | Pasta |
|---|---|---|---|
| **Poco X6 Pro** e Androids | Termux (nativo, sem root) | ❌ sobre o Android | `edicoes/termux/` |
| Android, distro cheia | Termux + `proot-distro debian` | ❌ (proot) | `edicoes/termux/` |
| **Raspberry Pi 3/4/5** | Pi OS 64-bit + instalador | ✅ **sim** | `edicoes/raspberry/` |
| SBC arm64 com UEFI / VM arm64 | ISO com `TOCAIA_ARCH=arm64` | ✅ | `edicoes/debian/` |
| Qualquer ARM64 c/ Docker | imagem multi-arch | — (container) | `edicoes/alpine/` |

## Sobre o Poco X6 Pro baremetal (a pergunta direta)

Não dá, hoje, de forma prática — e o motivo é o aparelho, não a TOCAIA:

- o **Dimensity 8300 Ultra** não tem porte mainline/postmarketOS pronto;
- a **GPU Mali** não tem driver livre maduro para um desktop;
- o **verified boot** da Xiaomi trava a troca do sistema.

O jeito real de usar no X6 Pro é o **Termux** (o `trem` roda nativo, é Python puro).
Para **baremetal ARM de verdade**, o **Raspberry Pi** é o alvo certo: boota do cartão
com a TOCAIA no metal. Ambos estão prontos neste repo.

## Por que isso funciona sem esforço

O `trem` e as ferramentas próprias são **stdlib pura**: o mesmo `.pyz` roda em x86 e
ARM sem recompilar. Só as ferramentas de terceiro com partes compiladas é que dependem
da plataforma — e essas entram sob demanda, com o `trem` avisando se faltar algo.

## Construir a imagem/container ARM

```
# container multi-arch (amd64 + arm64), publica no GHCR pelo CI em tags
docker buildx build --platform linux/amd64,linux/arm64 -f edicoes/alpine/Dockerfile -t tocaia:1.0 .

# ISO Debian arm64 (para SBC com UEFI ou VM arm64)
TOCAIA_ARCH=arm64 sudo edicoes/debian/build.sh
```

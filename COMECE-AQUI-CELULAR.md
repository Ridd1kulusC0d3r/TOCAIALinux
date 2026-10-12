# Comece aqui — TOCAIA no celular ("Matula")

Você vai ter o desktop da TOCAIA no seu Android em 3 passos. Não precisa de root nem de saber Linux.
Feito pensando no **POCO X6 Pro**; funciona em quase todo Android 10+ com processador de 64 bits.

## Passo 1 — Instale 3 apps (fora da Play Store)

| App | De onde |
|---|---|
| **Termux** | F-Droid: https://f-droid.org/packages/com.termux/ |
| **Termux:Widget** | F-Droid (mesma loja do Termux) |
| **Termux:X11** | GitHub: https://github.com/termux/termux-x11/releases → tag *nightly* → `termux-x11-universal-debug.apk` |

O Android vai pedir para "permitir apps desconhecidos": permita só para o navegador que você usou.

## Passo 2 — Um comando

No Wi-Fi, abra o Termux e cole:

```
curl -fsSL https://raw.githubusercontent.com/Ridd1kulusC0d3r/TOCAIALinux/main/celular/instalar.sh | bash
```

Leva uns 30 a 40 minutos (baixa ~1 a 1,5 GB). No fim, aparece o **doutor** com `ok` em cada item.

## Passo 3 — Botões na tela inicial

Segure num espaço vazio da tela inicial → **Widgets** → **Termux:Widget** → arraste.
Toque em **TOCAIA Desktop**. Gire o celular. Pronto: é o desktop da TOCAIA, com o menu pelas 6 fases.

Também importante: *Configurações → Apps → Termux → Economia de bateria → Sem restrições*.

## E no PC ou na TV?

- **TV:** toque em **TOCAIA na TV** e escolha a TV na tela de Transmitir (precisa de Miracast).
- **PC (o "DeX" de verdade):** instale Python 3, adb e scrcpy 3.0+ no computador, ligue a Depuração USB no celular e dê dois cliques em `celular/pc/TOCAIA-DeX`. O desktop abre numa janela do PC e o celular continua livre.

## Quero mais

- Guia completo, com root e com sistema novo: [`docs/CELULAR.md`](docs/CELULAR.md)
- Manual ilustrado: [`docs/manual-celular.html`](docs/manual-celular.html) (abra no navegador)

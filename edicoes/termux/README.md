# TOCAIA no Poco X6 Pro (e qualquer Android ARM64) — edição Termux

## Antes de tudo: a verdade sobre "baremetal" no Poco X6 Pro

Instalar uma distro Linux **baremetal** (no metal, substituindo o Android) no Poco
X6 Pro **não é viável hoje**, e não é limitação de preguiça:

- o SoC **Dimensity 8300 Ultra** não tem porte mainline/**postmarketOS** pronto;
- a GPU **Mali** não tem driver livre maduro para desktop;
- o **bootloader/verified boot** da Xiaomi trava a troca do sistema.

Forçar isso daria um trabalho enorme e provavelmente **nem bootaria**. O caminho que
**funciona de verdade** para ter a TOCAIA no seu celular é o **Termux**: um ambiente
Linux ARM64 nativo que roda **sobre** o Android, sem root. É leve, é real, e o `trem`
roda nativo porque é Python puro (stdlib).

Se o que você quer é **baremetal ARM de verdade**, o alvo certo é um **Raspberry Pi**
— veja `edicoes/raspberry/`.

## Instalação (5 minutos)

1. Instale o **Termux** pela **F-Droid** (https://f-droid.org) — a versão da Play Store
   é antiga e quebra. Abra o app.
2. Atualize e instale o básico:
   ```
   pkg update && pkg upgrade -y
   pkg install -y git python
   ```
3. Baixe a TOCAIA e rode o instalador:
   ```
   git clone https://github.com/Ridd1kulusC0d3r/TOCAIALinux
   bash TOCAIALinux/edicoes/termux/instalar.sh
   ```
4. Abra um novo terminal (ou `source ~/.bashrc`). Deve aparecer:
   `◆ uai, sô — TOCAIA OSINT Linux 1.0 "Tropeiro" ...`

## Usando

```
trem                    # o catálogo, por fase
trem fases              # a doutrina
trem relogio --demo     # padrão de vida (OSINT)
trem silencio TOCAIA/opt/tocaia/wargames/demo/alerts-demo.json   # detecção pela ausência
trem opsec              # checklist de OPSEC (checagem local)
trem placar <cenario.json> <alerts.json>                         # war game
trem manifesto --saida man.json                                  # cadeia de custódia
```

As ferramentas próprias (stdlib) rodam nativas. As de terceiro são instaladas sob
demanda com `pip` dentro do Termux na primeira vez (algumas com partes compiladas
podem exigir `pkg install` de uma dependência — o `trem` avisa).

## Dicas de celular

- **Teclado**: no Termux, `Volume baixo + Q` mostra uma barra com Esc, Tab, setas.
- **Arquivos do celular**: `termux-setup-storage` cria `~/storage/` apontando para a
  memória do aparelho — coloque seus CSV/JSON lá e aponte o `trem` para eles.
- **Atalho na tela inicial**: o Termux:Widget (F-Droid) deixa você criar um ícone que
  abre direto num script `trem`.
- **Quer a distro cheia (Debian) no celular?** `pkg install proot-distro` e depois
  `proot-distro install debian` — aí dá para rodar a edição Debian inteira por dentro.

Fonte pública · zero interação · base legal. Ler não é invadir. Esperar não é emboscar.

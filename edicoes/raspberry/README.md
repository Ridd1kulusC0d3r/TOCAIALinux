# TOCAIA baremetal no Raspberry Pi (ARM64)

Aqui o "no metal" é real: o Raspberry Pi boota do cartão SD com a TOCAIA rodando
direto no hardware. Funciona em **Pi 3, 4 e 5** (64-bit).

## Caminho recomendado — Raspberry Pi OS + instalador (confiável)

1. No seu PC, use o **Raspberry Pi Imager** (https://www.raspberrypi.com/software/).
2. Escolha **Raspberry Pi OS (64-bit)** — a versão **Lite** para só terminal, ou a
   completa se quiser desktop. Grave no cartão (16 GB+).
3. No próprio Pi, depois do primeiro boot:
   ```
   sudo apt update && sudo apt install -y git
   git clone https://github.com/Ridd1kulusC0d3r/TOCAIALinux
   sudo ./TOCAIALinux/edicoes/raspberry/instalar.sh            # só o trem
   sudo ./TOCAIALinux/edicoes/raspberry/instalar.sh --desktop  # + tema/wallpaper
   ```
4. Abra um novo terminal: `trem`.

Esse caminho é o mais robusto porque o Pi OS já traz o **firmware, o bootloader e os
drivers** certos do Pi — você só assenta a TOCAIA por cima.

## Caminho avançado — imagem arm64 da ISO

A ISO Debian live (`edicoes/debian/`) também constrói em **arm64**: no `auto/config`,
troque `--architectures amd64` por `--architectures arm64` e rode o build numa máquina
arm64 (ou com qemu). Isso gera uma imagem para **SBCs arm64 com UEFI**. O Raspberry Pi
**não** usa UEFI por padrão, então para o Pi prefira o caminho recomendado acima; a
imagem arm64 da ISO serve a placas como as da linha com UEFI (ex.: algumas Rockchip) e
a VMs arm64.

## Container arm64 (sem gravar cartão)

Se o Pi já roda outro SO, a imagem de container também é arm64 e roda na hora:
```
docker run --rm -it ghcr.io/ridd1kulusc0d3r/tocaia:latest
```

## O que funciona bem no Pi

- O `trem` e todas as ferramentas próprias (stdlib) — leves, rodam até no Pi 3.
- `silencio`, `placar` e o **wargames** — ótimo para um laboratório de detecção
  portátil (um Pi na mochila rodando o juiz do war game).
- OSINT passivo (`relogio`, `opsec`, `whois`, `dig`, `exiftool`).

Fonte pública · zero interação · base legal.

# celular/ — edição Android "Matula"

O "modo DeX" da TOCAIA, recriado com peças abertas: Debian 13 + Xfce (proot ou chroot) dentro do Termux,
Termux:X11 como tela, e celular, PC (monitor virtual do scrcpy) ou TV (Miracast) como monitor.
Para leigos: [COMECE-AQUI-CELULAR.md](../COMECE-AQUI-CELULAR.md). Guia completo: [docs/CELULAR.md](../docs/CELULAR.md).

```
instalar.sh             instalação em um comando (Termux)
tocaia_celular.py       orquestrador no celular, stdlib: doutor | instalar | desktop | parar | atalhos | dispositivo
chroot/                 entrar-chroot.sh e sair-chroot.sh (modo com root, via su)
rootfs/                 vai para dentro do Debian: tocaia-setup.sh (usuário, grupos de rede do Android, locale)
                        e o papel de parede que se aplica em qualquer monitor
atalhos/                botões do Termux:Widget (@TOCAIA@ é trocado pelo caminho real)
pc/tocaia_pc.py         lado do PC, stdlib: checar | preparar | dex | espelhar | parear | conectar | reverter
pc/TOCAIA-DeX (...)     lançadores de dois cliques (Windows, Mac, Linux)
```

## Decisões de projeto

- **Uma fonte só.** Os pacotes do Debian saem da lista da ISO (`iso/config/package-lists/tocaia.list.chroot`)
  menos o que é de pendrive; tema e menu saem de `tema/gerar_tema.py` e `iso/gerar_menu.py`. Mudou na ISO, muda no celular.
- **Um Debian, dois jeitos de entrar.** O chroot usa o rootfs que o `proot-distro` baixou. Dá para alternar sem reinstalar.
- **Planos antes de comandos.** Cada ação é uma lista de `Passo`; `--simular` mostra tudo sem executar, e os testes conferem os planos.
- **Ficha do aparelho no manifesto.** `getprop` → `/opt/tocaia/dispositivo.json` → `trem manifesto` (modelo, Android, patch, verified boot, bootloader).

## Testes

`python3 -m unittest testes.test_celular -v` (da raiz do repositório).

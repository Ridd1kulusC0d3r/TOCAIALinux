# Guia do sistema com interface (edição Debian + Xfce) — do zero

Esta é a TOCAIA **completa**: um sistema operacional de verdade, com interface
gráfica bonita, menu, janelas e wallpaper — mais leve que Kali e Parrot, e com a
sua cara. É baseada no **Debian**, a mesma base do Kali e do Parrot, então tudo que
é OSINT funciona aqui.

---

## 1. Entendendo o que é o Debian (e o Xfce)

- **Debian** é uma das distribuições Linux mais antigas e estáveis. Kali e Parrot
  são Debian "turbinados" — então ao aprender Debian, você entende a base deles.
- O gerenciador de pacotes é o **`apt`**: `sudo apt install nome`.
- **Xfce** é o ambiente gráfico (as janelas, o menu, o painel). Escolhemos ele por
  ser **leve e rápido**. A beleza vem do tema TOCAIA, não de efeitos pesados.

---

## 2. Gravar a ISO e dar boot (modo live, sem instalar nada)

> Modo live = o sistema roda do pendrive, sem tocar no seu HD. Ideal para aprender.

1. **Baixe** a ISO (`dist/TOCAIA-OSINT-Linux-1.0-Tropeiro-amd64.iso`, gerada pelo CI).
2. **Grave** num pendrive (8 GB+) com o **balenaEtcher** (https://etcher.balena.io) —
   ele é o mais simples: escolha a ISO, escolha o pendrive, clique em *Flash*.
3. **Dê boot** pelo pendrive: reinicie e aperte a tecla de boot do seu PC
   (geralmente **F12**, **F10**, **Esc** ou **F2**; em placa ASUS costuma ser F8).
4. No menu do GRUB (a tela escura com "TOCAIA"), escolha a primeira opção e Enter.
5. O sistema entra sozinho (autologin) no usuário **analista**.

**Sem pendrive?** Você pode rodar a ISO numa máquina virtual (**VirtualBox** grátis):
crie uma VM Linux/Debian 64-bit, 2 GB+ de RAM, e aponte o "disco óptico" para a ISO.

---

## 3. A tela inicial — o que você vê

- **Painel** no topo: o botão **TOCAIA** (menu), janelas abertas, relógio, rede, bateria.
- **Wallpaper**: a mira e os círculos concêntricos, com o wordmark em degradê.
- **Menu TOCAIA** (clique no canto superior esquerdo): aqui está a novidade —

### O menu segue a doutrina, não o tipo de ferramenta

Em vez de "Information Gathering", "Web", "Password Attacks" (como no Kali), o menu da
TOCAIA tem **as seis fases**:

```
TOCAIA
├── Manual da TOCAIA
├── Terminal TOCAIA
├── 1 · T — Traçar
├── 2 · O — Observar
├── 3 · C — Cercar
├── 4 · A — Aguardar
├── 5 · I — Interpretar
└── 6 · A — Atribuir
```

Navegar no menu, de cima para baixo, é percorrer o método de uma investigação.

---

## 4. Primeiros comandos (terminal dentro da interface)

Abra o **Terminal TOCAIA** (pelo menu ou com o atalho). Os comandos são os mesmos do
guia Alpine, mais o `apt` para instalar programas:

```
trem                      # catálogo
trem relogio --demo       # roda o RELÓGIO
sudo apt update           # atualiza a lista de pacotes
sudo apt install nmap     # instala um programa do Debian
```

Diferença para o Alpine: aqui é **`apt`** (Debian), lá é **`apk`** (Alpine). O `trem`
já sabe disso e te dá a dica certa quando falta um binário.

---

## 5. Instalando no HD (quando quiser pra valer)

O modo live é ótimo para aprender, mas tudo some ao desligar. Quando decidir instalar:
- Use o instalador do Debian (Calamares/d-i), se incluído numa build futura, **ou**
- Instale um Debian normal e aplique o tema TOCAIA por cima rodando
  `sudo python3 tema/gerar_tema.py --destino /` (sem precisar reinstalar nada).

> Dica de segurança: para OSINT, muita gente prefere **não instalar** e usar sempre
> live + um pendrive de persistência criptografada. A TOCAIA live já nasce para isso.

---

## 6. Trocando a cara (o tema é seu)

Todo o visual sai de um arquivo só: `tema/tokens.json`. Mude uma cor lá, rode
`python3 tema/gerar_tema.py --destino ./saida && ...`, e GTK, janelas, terminal,
wallpaper e tela de login se atualizam juntos. Nenhuma edição manual de tema.

---

## 7. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| PC não dá boot pelo pendrive | ordem de boot / Secure Boot | entre no menu de boot (F12…); se preciso, desative Secure Boot |
| tela preta após o GRUB | driver de vídeo | no GRUB, tecle `e`, acrescente `nomodeset` na linha `linux`, F10 |
| sem Wi-Fi | firmware do adaptador | a ISO já traz `non-free-firmware`; alguns exigem cabo na 1ª vez |
| quero mais ferramentas | base enxuta de propósito | `sudo apt install ...` ou `trem <ferramenta>` (sob demanda) |

---

Para a instalação detalhada com telas anotadas e diagramas, abra o **Manual Ilustrado**
(`docs/manual/index.html`). Para saber quais das suas ferramentas entram em cada fase,
veja **PROJETOS.md**.

# Guia do sistema de terminal (edição Alpine) — do zero

Esta é a TOCAIA **sem interface gráfica**: só o terminal. É a versão mais leve e
universal — roda em Docker, WSL, Raspberry Pi e na nuvem. É também o melhor lugar
para **aprender Linux de verdade**, porque aqui tudo é comando e nada se esconde.

Se "terminal" ainda te assusta: relaxa. São uns 15 comandos que resolvem 90% do dia.

---

## 1. Entendendo o que é o Alpine

- **Alpine Linux** é uma distribuição minúscula (a base tem ~8 MB). Foi feita para
  containers e sistemas enxutos.
- Ela usa **musl** no lugar da **glibc** (a biblioteca C padrão). Para você, usuário,
  isso é invisível — só importa que algumas ferramentas pesadas de terceiro podem
  não compilar. Como as **suas** ferramentas são stdlib puro, isso não te afeta.
- O gerenciador de pacotes é o **`apk`** (não `apt`). Instalar algo: `apk add nome`.

---

## 2. Abrindo a TOCAIA Alpine

**Com Docker (qualquer sistema):**
```
docker run --rm -it ghcr.io/ridd1kulusc0d3r/tocaia:latest
```
Você cai num shell já saudando: `uai, sô — ...`.

**Com WSL (Windows, sem máquina virtual):**
```
wsl --import TOCAIA C:\WSL\TOCAIA dist\TOCAIA-WSL.tar.gz
wsl -d TOCAIA
```

**`--rm`** apaga o container ao sair (nada fica sujo). Para guardar seus arquivos
entre sessões, monte uma pasta sua:
```
docker run --rm -it -v "$HOME/TOCAIA-casos:/home/analista/casos" ghcr.io/ridd1kulusc0d3r/tocaia:latest
```
Tudo que você salvar em `casos/` dentro do container aparece em `~/TOCAIA-casos` no seu PC.

---

## 3. Os comandos de Linux que você precisa (e só esses, no começo)

| Comando | O que faz | Exemplo |
|---|---|---|
| `ls` | lista arquivos | `ls casos/` |
| `cd` | entra numa pasta | `cd casos/demo-bx7` |
| `pwd` | mostra onde você está | `pwd` |
| `cat` | mostra o conteúdo de um arquivo | `cat postagens.csv` |
| `less` | lê um arquivo rolando (sai com `q`) | `less postagens.csv` |
| `nano` | editor de texto simples (salva com Ctrl+O, sai com Ctrl+X) | `nano notas.txt` |
| `cp` / `mv` / `rm` | copia / move / apaga | `cp a.csv b.csv` |
| `mkdir` | cria pasta | `mkdir caso-joao` |
| `grep` | procura texto dentro de arquivos | `grep "19:" postagens.csv` |
| `|` (pipe) | liga a saída de um comando na entrada de outro | `trem | grep pronta` |
| `>` | salva a saída num arquivo | `trem lista > ferramentas.txt` |

> **Dica de ouro:** aperte **Tab** para completar nomes e **↑** para repetir comandos.

---

## 4. Usando a TOCAIA no terminal

```
trem                    # o catálogo inteiro
trem fases              # a doutrina
trem relogio --demo     # roda o RELÓGIO no caso de exemplo
trem relogio casos/demo-bx7/postagens.csv --html rel.html --json rel.json
trem manifesto --saida manifesto.json
trem doutor
```

Instalando uma ferramenta de terceiro (só na primeira vez):
```
trem sherlock um_usuario
trem maigret um_usuario --html
```

Precisa de um pacote de sistema que não veio? Use o `apk`:
```
apk add nmap        # (dentro do container, como root: use 'doas' ou rode como root)
```

---

## 5. Exercício guiado (10 minutos)

1. Entre na TOCAIA: `docker run --rm -it ghcr.io/ridd1kulusc0d3r/tocaia:latest`
2. Veja as fases: `trem fases`
3. Rode o caso de exemplo: `trem relogio --demo`
4. Olhe os achados: repare no **silêncio de 7 dias** — "o silêncio tem data de início".
5. Gere o relatório: `trem relogio casos/demo-bx7/postagens.csv --html /home/analista/casos/rel.html`
6. Gere o manifesto: `trem manifesto --saida /home/analista/casos/manifesto.json`
7. Veja o arquivo: `cat /home/analista/casos/manifesto.json | less`
8. Saia: `exit`

Se você montou o volume (`-v`), `rel.html` e `manifesto.json` estarão em `~/TOCAIA-casos`
no seu computador, prontos para abrir.

---

## 6. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `docker: command not found` | Docker não instalado | instale o Docker Desktop/Engine |
| `Cannot connect to the Docker daemon` | Docker não está rodando | abra o Docker Desktop e espere |
| ferramenta de terceiro falha ao instalar | sem internet na primeira vez | conecte e rode de novo |
| mudei um arquivo e sumiu ao sair | não montou volume | use `-v "$HOME/TOCAIA-casos:/home/analista/casos"` |

---

Quando estiver confortável aqui, o **GUIA-DEBIAN.md** te leva para a versão com
interface gráfica — os mesmos comandos funcionam, mas com janelas e menu por cima.

# Comece aqui

Você vai aprender a usar a TOCAIA em 3 passos. Não precisa saber Linux.

## Passo 1 — Escolha como quer rodar

- **Quero só testar agora, no meu computador:** instale o Python 3 (python.org) e dê **dois cliques** no lançador:
  - Windows: `iniciar.bat`
  - Mac: `iniciar.command`
  - Linux: `iniciar.sh`
- **Não quero instalar nada:** abra o notebook `nuvem/TOCAIA_Colab.ipynb` no Google Colab e aperte o play em cada célula.
- **Quero no meu celular Android:** siga o [COMECE-AQUI-CELULAR.md](COMECE-AQUI-CELULAR.md). Dá para usar na tela do celular, no PC ou na TV.
- **Quero a distro completa, com tela bonita:** baixe a ISO na aba *Releases* do GitHub, grave num pendrive com o balenaEtcher ou o Rufus e dê boot por ele.

## Passo 2 — Conheça o `trem`

Abra um terminal e digite:

```
trem
```

Ele mostra as ferramentas agrupadas pelas 6 fases da investigação. Para rodar uma: `trem opsec`.

## Passo 3 — Jogue a primeira rodada do war game

```
trem placar /opt/tocaia/wargames/cenarios/rodada1-tropeiro-x-atalaia.json /opt/tocaia/wargames/demo/alerts-demo.json
```

(Fora da ISO/container, use os caminhos `wargames/...` da pasta do projeto.)

Você vai ver quem venceu, quais ataques passaram despercebidos e quanto tempo a defesa levou para detectar.

## Deu problema?

Veja a seção **Solução de problemas** do `docs/manual.html`.

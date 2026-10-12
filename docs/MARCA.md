# Marca nas telas — onça na espreita e face de olhos ciano

As artes da marca (`assets/marca/`) são integradas às telas do sistema por
`assets/gerar_marca.py`, que roda **depois** do `tema/gerar_tema.py` (o
`iso/construir-iso.sh` já encadeia os dois).

## O que ele faz

- **Wallpaper** (`usr/share/backgrounds/tocaia/tocaia.svg`) passa a ser a **onça na
  espreita** com o wordmark TOCAIA. Como o desktop (hook `9000`) e o login (greeter)
  já apontam para esse arquivo, os dois recebem a arte sem mais nada.
- O wallpaper **vetorial** original é preservado como `tocaia-mira.svg`.
- **Variante** `tocaia-face.svg` (a face de olhos ciano) fica disponível para quem
  preferir trocar.
- **Login** ganha `login.png` (a face centralizada) — opcional: aponte o greeter para
  ele em `tema/gerar_tema.py` se quiser a face em vez da onça no login.
- **Ícone do app** (`hicolor/<tam>/apps/tocaia.png` e `pixmaps/tocaia.png`) passa a ser
  a face — aparece no menu e no painel. O hook `9100-marca` atualiza o cache de ícones.

As cores vêm de `tema/paleta.json` (a mesma fonte do resto do tema); os olhos ciano da
arte já coincidem com a menta da paleta. Precisa de Pillow no build (o `construir-iso.sh`
instala se faltar; sem ele, mantém o wallpaper vetorial).

## Trocar a arte

Troque os arquivos em `assets/marca/` (mantendo os nomes) e rode o build de novo.
Para usar a face no login, edite a linha `background=` em `tema/gerar_tema.py` para
`/usr/share/backgrounds/tocaia/login.png`.

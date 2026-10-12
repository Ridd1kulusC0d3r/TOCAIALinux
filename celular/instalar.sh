#!/data/data/com.termux/files/usr/bin/bash
# TOCAIA "Matula" — instalação em um comando, dentro do Termux:
#
#   curl -fsSL https://raw.githubusercontent.com/Ridd1kulusC0d3r/TOCAIALinux/main/celular/instalar.sh | bash
#
# Baixa o repositório para ~/TOCAIALinux, instala tudo (sem root) e cria os
# botões da tela inicial. Pode rodar de novo: ele só atualiza.
set -e
REPO="https://github.com/Ridd1kulusC0d3r/TOCAIALinux.git"
DESTINO="$HOME/TOCAIALinux"

printf '\n  \033[38;2;94;234;212mTOCAIA "Matula"\033[0m — a matula do tropeiro, no bolso.\n\n'

pkg install -y git python >/dev/null
if [ -d "$DESTINO/.git" ]; then
  git -C "$DESTINO" pull --ff-only
else
  git clone --depth 1 "$REPO" "$DESTINO"
fi

python "$DESTINO/celular/tocaia_celular.py" instalar
python "$DESTINO/celular/tocaia_celular.py" atalhos
python "$DESTINO/celular/tocaia_celular.py" doutor

printf '\n  Pronto. Toque no botão "TOCAIA Desktop" na tela inicial\n'
printf '  (ou rode: python ~/TOCAIALinux/celular/tocaia_celular.py desktop)\n\n'

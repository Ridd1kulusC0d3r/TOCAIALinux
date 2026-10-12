# Saudação da TOCAIA ao abrir um shell (container, WSL ou ISO).
export TREM_HOME="${TREM_HOME:-/opt/tocaia}"
if [ -t 1 ] && [ -z "$TOCAIA_SAUDOU" ]; then
  export TOCAIA_SAUDOU=1
  printf '\n  \033[38;2;94;234;212mTOCAIA OSINT Linux\033[0m — "Tropeiro"\n'
  printf '  Use com ética: fonte aberta, sem invadir, sem enganar, sem assediar.\n'
  printf '  Digite \033[1mtrem\033[0m para ver as ferramentas por fase.\n\n'
fi

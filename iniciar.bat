@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% build.py || goto erro
%PY% -m unittest discover -s testes || goto erro
%PY% trem\trem.py
%PY% trem\trem.py placar wargames\cenarios\rodada1-tropeiro-x-atalaia.json wargames\demo\alerts-demo.json --relatorio placar.md
echo.
echo Relatorio salvo em placar.md
pause
exit /b 0
:erro
echo Algo deu errado. Instale o Python 3 em python.org e marque "Add to PATH".
pause

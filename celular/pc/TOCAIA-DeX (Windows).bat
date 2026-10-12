@echo off
REM TOCAIA "Matula" - o PC como tela do celular. Dois cliques.
REM Precisa de Python 3, adb e scrcpy (o menu "checar" mostra como instalar).
title TOCAIA Matula - modo DeX
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul || (echo Instale o Python 3 em python.org ^(marque Add to PATH^). & pause & exit /b 1)
python tocaia_pc.py
pause

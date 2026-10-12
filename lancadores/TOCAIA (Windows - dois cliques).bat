@echo off
REM ============================================================
REM  TOCAIA OSINT Linux - lancador de dois cliques (Windows)
REM  Precisa do Docker Desktop instalado e aberto.
REM ============================================================
title TOCAIA OSINT Linux
chcp 65001 >nul
echo.
echo   ^> TOCAIA OSINT Linux - uai, so.
echo.

where docker >nul 2>nul
if errorlevel 1 (
  echo   [!] Docker nao encontrado. Instale o Docker Desktop:
  echo       https://www.docker.com/products/docker-desktop/
  echo.
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo   [!] O Docker Desktop esta instalado mas nao esta rodando.
  echo       Abra o Docker Desktop e espere ficar verde, depois rode de novo.
  echo.
  pause
  exit /b 1
)

echo   Baixando/abrindo a imagem (so demora na primeira vez)...
echo.
docker run --rm -it -v "%USERPROFILE%\TOCAIA-casos:/home/analista/casos" ghcr.io/ridd1kulusc0d3r/tocaia:latest
pause

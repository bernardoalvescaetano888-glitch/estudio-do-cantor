@echo off
chcp 65001 >nul
title Estúdio do Cantor - Instalador
echo ============================================
echo   ESTUDIO DO CANTOR - Instalacao de pacotes
echo ============================================
echo.
python -m pip install --upgrade pip
echo.
echo [1/2] Instalando PyTorch (versao CPU, mais leve)...
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
echo.
echo [2/2] Instalando os demais pacotes...
python -m pip install -r requirements.txt
echo.
echo ============================================
echo   Instalacao concluida!
echo   Rode executar.bat para abrir o app.
echo ============================================
pause

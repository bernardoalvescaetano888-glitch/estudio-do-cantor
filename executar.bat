@echo off
chcp 65001 >nul
title Estudio do Cantor
cd /d "%~dp0"
python app.py
if errorlevel 1 (
  echo.
  echo Ocorreu um erro. Verifique se executou instalar.bat antes.
  pause
)

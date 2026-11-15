#!/usr/bin/env bash
# Estúdio do Cantor — instalador para macOS e Linux
set -e
cd "$(dirname "$0")"
echo "============================================"
echo "  ESTÚDIO DO CANTOR — instalação de pacotes"
echo "============================================"
python3 -m pip install --upgrade pip
echo "[1/2] PyTorch (CPU)..."
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
echo "[2/2] Demais pacotes..."
python3 -m pip install -r requirements.txt
echo "Instalação concluída! Rode: ./executar.sh"

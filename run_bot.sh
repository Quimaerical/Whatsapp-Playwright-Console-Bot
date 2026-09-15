#!/usr/bin/env bash
set -e

echo "========================================================"
echo "      BOT DE WHATSAPP CON PLAYWRIGHT Y PATRONES        "
echo "========================================================"
echo ""
echo "Ejecutando el bot con PDM..."
pdm run python main.py "$@"
echo ""
echo "========================================================"
echo "      Ejecución finalizada."
echo "========================================================"
echo ""
read -p "Presiona enter para salir..."

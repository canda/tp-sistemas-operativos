#!/bin/bash
set -e

cd -- "$(dirname -- "$0")"

# Insalar GCC si no está instalado.
if ! command -v gcc &> /dev/null; then

    echo "GCC no está instalado. Instalando..."

    sudo dnf install -y gcc

fi
# Compilar el programa para ejecutarlo en Red Hat.
gcc -O0 -static unidad-1.c -o unidad-1

# Generar ensamblador desde el código C, sin optimizaciones.
objdump -d unidad-1 > unidad-1.s

# Mostrar el ensamblador generado.
cat ./unidad-1.s
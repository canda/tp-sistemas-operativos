#!/bin/bash
set -e

# Trabajar desde la carpeta del script.
cd -- "$(dirname -- "$0")"

# Instalar GCC si no está instalado.
if ! command -v gcc &> /dev/null; then
    echo "GCC no está instalado. Instalando..."
    sudo dnf install -y gcc
fi

# Compilar el programa C. Si falla, no ejecutar un binario anterior.
gcc -Wall -Wextra -O0 unidad-6.c -o unidad-6

# Ejecutar el programa compilado.
./unidad-6

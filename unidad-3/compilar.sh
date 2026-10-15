#!/bin/bash

# Insalar GCC si no está instalado.
if ! command -v gcc &> /dev/null; then

    echo "GCC no está instalado. Instalando..."

    sudo dnf install -y gcc
fi

# Dar permiso de ejecución al script
chmod +x "$0"

# Compilar el programa en C
gcc -Wall -Wextra -O0 paginacion.c -o paginacion

# Si la compilación falla, no continuar
if [ $? -ne 0 ]; then
    echo "Error: no se pudo compilar paginacion.c"
    exit 1
fi

# Dar permiso de ejecución al binario generado
chmod +x paginacion

# Ejecutar el programa
./paginacion
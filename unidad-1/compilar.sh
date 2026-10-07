#!/bin/bash
set -e
cd -- "$(dirname -- "$0")"

# Compilar el programa para ejecutarlo en Red Hat.
gcc -O0 -o ./unidad-1 ./unidad-1.c

# Generar ensamblador desde el código C, sin optimizaciones.
gcc -S -O0 ./unidad-1.c -o ./unidad-1.s

# Mostrar el ensamblador generado.
cat ./unidad-1.s

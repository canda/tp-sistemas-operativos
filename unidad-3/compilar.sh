#!/bin/bash

# Verificar GCC
if ! command -v gcc &> /dev/null; then
    echo "GCC no está instalado. Instalando..."
    sudo dnf install -y gcc
fi

# Compilar
gcc -Wall -Wextra -O0 paginacion.c -o paginacion
if [ $? -ne 0 ]; then
    echo "Error: no se pudo compilar paginacion.c"
    exit 1
fi
chmod +x paginacion

# --- INICIO DEL EJERCICIO PRÁCTICO ---
echo "======================================================"
echo "Escenario: Simulando un pico de consumo de memoria"
echo "de un servicio backend para observar la paginación."
echo "======================================================"

echo -e "\n[Sistema] Memoria antes de la ejecución (free -h):"
free -h

# Ejecutar el programa en C en segundo plano
./paginacion &
C_PID=$!

# Esperar a que el programa en C asigne la memoria (basado en sus sleeps)
sleep 5

echo -e "\n[Sistema] Monitoreando el proceso con PID $C_PID (ps):"
# Mostrar usuario, PID, % de memoria, Tamaño Virtual (VSZ) y Memoria Residente (RSS)
ps -o user,pid,%mem,vsz,rss,comm -p $C_PID

echo -e "\n[Sistema] Estadísticas de memoria virtual (vmstat):"
vmstat 1 3

# Esperar a que el programa en C termine naturalmente
wait $C_PID

echo -e "\n[Sistema] Memoria después de la liberación (free -h):"
free -h
echo "======================================================"
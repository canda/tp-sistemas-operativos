#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

# Instalar sólo los paquetes correspondientes a herramientas faltantes.
paquetes=()
command -v gcc >/dev/null 2>&1 || paquetes+=(gcc)
command -v taskset >/dev/null 2>&1 || paquetes+=(util-linux)
command -v date >/dev/null 2>&1 || paquetes+=(coreutils)
command -v awk >/dev/null 2>&1 || paquetes+=(gawk)

if (( ${#paquetes[@]} > 0 )); then
    echo "Instalando herramientas faltantes: ${paquetes[*]}"
    if (( EUID == 0 )); then
        dnf install -y "${paquetes[@]}"
    else
        sudo dnf install -y "${paquetes[@]}"
    fi
fi

# Sin optimizaciones: conservar el bucle de suma.
gcc -Wall -Wextra -O0 unidad-2.c -o unidad-2

# Respetar las CPU que el laboratorio permite usar a este proceso.
cpus=$(LC_ALL=C taskset -pc "$$")
cpus=${cpus##*: }
primera_cpu=${cpus%%[,-]*}

echo "CPU lógicas permitidas: $cpus"
echo "Cada modalidad ejecuta 10 veces la misma suma."

medir() {
    local modo=$1 afinidad=$2 inicio fin pid
    local pids=()
    echo
    echo "=== $modo ==="
    inicio=$(date +%s%N)

    for (( tarea=1; tarea<=10; tarea++ )); do
        if [[ "$modo" == "Secuencial" ]]; then
            taskset -c "$afinidad" ./unidad-2
        else
            taskset -c "$afinidad" ./unidad-2 &
            pids+=("$!")
        fi
    done

    # Esperar a todos y detectar errores en cualquiera de los procesos.
    local fallo=0
    for pid in "${pids[@]}"; do
        wait "$pid" || fallo=1
    done
    if (( fallo )); then
        echo "Falló un proceso; no se generará un reporte válido." >&2
        exit 1
    fi

    fin=$(date +%s%N)
    duracion=$((fin - inicio))
}

medir "Secuencial" "$primera_cpu"
secuencial=$duracion
medir "Pseudoparalela" "$primera_cpu"
pseudoparalela=$duracion

paralela=0
if [[ "$cpus" == "$primera_cpu" ]]; then
    echo
    echo "Paralela omitida: sólo hay una CPU lógica permitida."
else
    medir "Paralela" "$cpus"
    paralela=$duracion
fi

echo
echo "=== REPORTE: tiempo total de las 10 tareas ==="
awk -v s="$secuencial" -v p="$pseudoparalela" -v r="$paralela" 'BEGIN {
    printf "%-20s %12s\n", "Modalidad", "Tiempo (s)"
    printf "%-20s %12.3f\n", "Secuencial", s / 1e9
    printf "%-20s %12.3f\n", "Pseudoparalela", p / 1e9
    if (r > 0) {
        printf "%-20s %12.3f\n", "Paralela", r / 1e9
        printf "\nAceleración paralela respecto de secuencial: %.2fx\n", s / r
    } else {
        printf "%-20s %12s\n", "Paralela", "No disponible"
    }
}'

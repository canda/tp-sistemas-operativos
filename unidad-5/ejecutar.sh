#!/bin/bash
set -e

cd -- "$(dirname -- "$0")"

# Instalar GCC si no está instalado.
if ! command -v gcc &> /dev/null; then
    echo "GCC no está instalado. Instalando..."
    sudo dnf install -y gcc
fi

gcc -O0 unidad-5.c -o unidad-5

# Disco principal del sistema (vda, sda o nvme0n1).
DISCO=/dev/$(lsblk -dno NAME,TYPE | awk '$2=="disk" && $1 !~ /^(zram|loop)/{print $1; exit}')

# Archivo de prueba de 2 MB.
head -c 2000000 /dev/urandom > prueba.bin

echo "=== Programa: tipo de dispositivo y uso de búfer ==="
./unidad-5 prueba.bin "$DISCO" /dev/null /dev/tty /dev/urandom

echo
echo "=== Número mayor -> driver (/proc/devices) ==="
MAYOR=$((16#$(stat -c '%t' "$DISCO")))
grep -E "^ *($MAYOR|1|5) " /proc/devices

echo
echo "=== Interrupciones del controlador de disco antes y después de escribir 100 MB ==="
contar() { grep -Ei "virtio|ahci|nvme|ata" /proc/interrupts | awk '{for(i=2;i<=NF;i++) if($i ~ /^[0-9]+$/) s+=$i} END{print s+0}'; }
ANTES=$(contar)
dd if=/dev/zero of=escritura.tmp bs=1M count=100 oflag=direct status=none
DESPUES=$(contar)
rm -f escritura.tmp
echo "Antes: $ANTES   Después: $DESPUES   Nuevas: $((DESPUES - ANTES))"

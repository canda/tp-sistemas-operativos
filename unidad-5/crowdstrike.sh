#!/bin/bash
cd -- "$(dirname -- "$0")"

gcc -O0 crowdstrike.c -o crowdstrike

echo "=== 1. Los drivers corren dentro del kernel ==="
echo "Módulos (drivers) cargados en el kernel: $(lsmod | tail -n +2 | wc -l)"
modinfo virtio_blk 2>/dev/null | grep -E '^(filename|description)' || lsmod | head -5
echo "El sistema está funcionando desde: $(uptime -p)"

echo
echo "=== 2. El error de CrowdStrike, simulado en MODO USUARIO ==="
./crowdstrike 21
echo "Código de salida: $?   (139 = el SO mató al proceso con SIGSEGV)"

echo
echo "=== 3. El sistema operativo sigue funcionando ==="
echo "Uptime: $(uptime -p)"
sudo dmesg 2>/dev/null | grep -i "crowdstrike.*segfault" | tail -1

echo
echo "=== 4. La versión corregida valida la cantidad de campos ==="
./crowdstrike 21 --validar || true

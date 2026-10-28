#!/bin/bash
DISCO="/dev/vdb"
PARTICION="/dev/vdb1"
PUNTO_MONTAJE="/mnt/datos"

# Crear partición de forma automatizada
echo -e "n\np\n1\n\n\nw" | fdisk "$DISCO"

# Formatear en XFS
mkfs.xfs -f "$PARTICION"

# Crear punto de montaje
mkdir -p "$PUNTO_MONTAJE"

# Obtener UUID y configurar persistencia en /etc/fstab
UUID=$(blkid -s UUID -o value "$PARTICION")
if [ -z "$UUID" ]; then
  echo "Error: No se pudo obtener el UUID."
  exit 1
fi

sed -i "\|$PUNTO_MONTAJE|d" /etc/fstab
echo "UUID=$UUID  $PUNTO_MONTAJE  xfs  defaults  0  0" >> /etc/fstab

# Aplicar y verificar
mount -a
df -h | grep "$PUNTO_MONTAJE"
echo "¡Listo! Disco configurado y montado correctamente."
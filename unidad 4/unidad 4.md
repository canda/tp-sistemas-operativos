# Unidad 4 – Almacenamiento y Sistema de Archivos en RHEL
**Objetivo:** Automatizar la creación de particiones, formateo con sistema de archivos XFS y montaje persistente mediante un script en el entorno de laboratorio Red Hat.
**Entorno:** Consola del laboratorio Red Hat (RHEL) del curso.

1. **Definición de variables y particionado:**
   El script define las rutas clave (`/dev/vdb`, `/dev/vdb1` y `/mnt/datos`) y utiliza `fdisk` mediante redirección de comandos (`echo -e` con `n`, `p`, `1`, etc.) para crear la partición primaria abarcando todo el disco virtual disponible.

2. **Formateo y estructura:**
   Se aplica `mkfs.xfs -f` sobre la partición recién creada para inyectar los metadatos del sistema de archivos XFS (estándar de Red Hat). A su vez, se crea el directorio de destino asegurando la ruta con `mkdir -p`.

3. **Persistencia en el arranque (`/etc/fstab`):**
   El programa consulta dinámicamente el UUID mediante `blkid`, limpia posibles entradas duplicadas en `/etc/fstab` usando `sed`, y añade la directiva de montaje automático basada en UUID con opciones por defecto (`defaults 0 0`).

4. **Validación:**
   Finalmente, se ejecuta `mount -a` para aplicar la tabla de particiones y se comprueba el montaje con `df -h` filtrando por el punto de montaje.

**Conclusión para el informe:**
La automatización mediante scripts agiliza las tareas administrativas de almacenamiento en entornos RHEL. El uso de UUID en `/etc/fstab` garantiza que el sistema reconozca y monte correctamente el dispositivo aun si cambian las asignaciones de nombres de hardware del kernel en futuros reinicios.
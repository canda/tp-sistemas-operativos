# Unidad 5: Entrada / Salida

Entorno: consola del laboratorio Red Hat del curso.

1. El programa `unidad-5.c` tiene dos partes:
   - **Tipo de dispositivo:** con la syscall `stat`, clasifica cada archivo de `/dev` como dispositivo de **bloque** o de **carácter** y muestra su número **mayor** (identifica al driver) y **menor** (identifica la unidad que maneja ese driver).
   - **Uso de búfer:** lee el mismo archivo de 2 MB con búferes de 1, 512, 4096 y 65536 bytes, y cuenta cuántas llamadas a `read` hacen falta y cuánto tarda cada caso.

2. Desde la carpeta `unidad-5`, ejecutar:

```
./ejecutar.sh
```

3. Salida de la primera parte:

```
/dev/vda       BLOQUE    mayor=254 menor=0
/dev/null      CARACTER  mayor=1   menor=3
/dev/tty       CARACTER  mayor=5   menor=0
/dev/urandom   CARACTER  mayor=1   menor=9
```

El script busca esos números mayores en `/proc/devices`, donde se ve qué driver corresponde a cada uno (por ejemplo, `254 virtblk` es el driver de disco de la máquina virtual y `1 mem` maneja `/dev/null` y `/dev/urandom`).

4. Salida de la segunda parte:

```
Bufer(B)  Llamadas read()  Tiempo
1         2000000          0.8825 s
512       3907             0.0024 s
4096      489              0.0005 s
65536     31               0.0003 s
```

Con búfer de 1 byte, el programa hace 2 millones de syscalls: 2 millones de cambios de modo usuario a modo kernel. Con 4 KB son 489 llamadas y tarda unas 1700 veces menos.

5. Por último, el script cuenta las interrupciones del controlador de disco en `/proc/interrupts`, escribe 100 MB sin pasar por la caché (`oflag=direct`) y vuelve a contar:

```
Antes: 13095   Después: 13197   Nuevas: 102
```

Cada interrupción nueva es el aviso del controlador a la CPU de que terminó una transferencia.

Conclusión para el informe: los dispositivos de bloque permiten acceder a cualquier bloque por su número; los de carácter entregan un flujo de bytes. El número mayor vincula cada archivo de `/dev` con su driver dentro del kernel. El disco transfiere los datos por DMA y avisa con una interrupción al terminar, sin ocupar a la CPU durante la copia. El búfer agrupa los datos para reducir la cantidad de syscalls y de accesos al dispositivo.

# Unidad 5: Entrada / Salida

El ejercicio tiene dos partes: la **Parte A** observa cómo Linux maneja los dispositivos, los drivers, el búfer y las interrupciones; la **Parte B** compara esos conceptos con un caso real, la caída mundial de CrowdStrike en 2024.

Entorno: consola del laboratorio Red Hat del curso (salidas obtenidas en `student@workstation`).

## Parte A: Dispositivos, drivers, búfer e interrupciones

1. El programa `unidad-5.c` tiene dos partes:
   - **Tipo de dispositivo:** con la syscall `stat`, clasifica cada archivo de `/dev` como dispositivo de **bloque** o de **carácter** y muestra su número **mayor** (identifica al driver) y **menor** (identifica la unidad que maneja ese driver).
   - **Uso de búfer:** lee el mismo archivo de 2 MB con búferes de 1, 512, 4096 y 65536 bytes, y cuenta cuántas llamadas a `read` hacen falta y cuánto tarda cada caso.

2. Desde la carpeta `unidad-5`, ejecutar:

```
chmod +x ejecutar.sh
./ejecutar.sh
```

3. Salida de la primera parte:

```
/dev/vda       BLOQUE    mayor=252 menor=0
/dev/null      CARACTER  mayor=1   menor=3
/dev/tty       CARACTER  mayor=5   menor=0
/dev/urandom   CARACTER  mayor=1   menor=9
```

El script busca esos números mayores en `/proc/devices`, donde se ve qué driver corresponde a cada uno (por ejemplo, `252 virtblk` es el driver de disco de la máquina virtual y `1 mem` maneja `/dev/null` y `/dev/urandom`).

4. Salida de la segunda parte:

```
Bufer(B)  Llamadas read()  Tiempo
1         2000000          0.5975 s
512       3907             0.0017 s
4096      489              0.0006 s
65536     31               0.0004 s
```

Con búfer de 1 byte, el programa hace 2 millones de syscalls: 2 millones de cambios de modo usuario a modo kernel. Con 4 KB son 489 llamadas y tarda unas 1000 veces menos.

5. Por último, el script cuenta las interrupciones del controlador de disco en `/proc/interrupts`, escribe 100 MB sin pasar por la caché (`oflag=direct`) y vuelve a contar:

```
Antes: 327624   Después: 327771   Nuevas: 147
```

Cada interrupción nueva es el aviso del controlador a la CPU de que terminó una transferencia.

## Parte B: Caso real – CrowdStrike (19 de julio de 2024)

### Cómo llegamos a la comparación

1. **Partimos de la teoría.** En la Parte A vimos que el disco usa el driver `virtblk` (número mayor 252), cargado dentro del kernel. Es la pregunta 17 del cuestionario: ¿los drivers forman parte del kernel? Nos preguntamos qué pasa en la práctica cuando un driver falla.
2. **Buscamos un caso real.** Consideramos ataques por DMA (Thunderclap) y problemas de búfer en bases de datos (fsyncgate de PostgreSQL). Elegimos CrowdStrike porque es el más conocido y el que mejor muestra el tema.
3. **Investigamos la causa técnica.** Leímos el análisis de causa raíz publicado por CrowdStrike (ver Fuentes).
4. **Nos hicimos una pregunta.** Leer fuera de un arreglo es un error que cualquier programa en C puede cometer: ¿qué pasa si hacemos lo mismo en un programa común en lugar de un driver?
5. **Lo reprodujimos en el laboratorio** con `crowdstrike.c` y `crowdstrike.sh`.
6. **Comparamos los resultados.**

### Qué pasó

El 19 de julio de 2024, CrowdStrike envió una actualización de configuración (el "Channel File 291") para su producto Falcon. Millones de computadoras con Windows mostraron la pantalla azul y no pudieron volver a arrancar; Microsoft estimó unos 8,5 millones de equipos afectados. Cayeron sistemas de aerolíneas, bancos y hospitales en todo el mundo.

- El sensor Falcon funciona como un **driver dentro del kernel** de Windows y se carga muy temprano en el arranque.
- Su intérprete de contenido estaba programado para recibir **20 campos**. La actualización usó por primera vez un **campo 21**.
- Al leer el campo 21, el driver leyó **fuera del arreglo** (*out-of-bounds read*).
- Como el error ocurrió en **modo kernel**, nadie pudo frenarlo y cayó todo el sistema. Como el driver se carga al arrancar, el equipo volvía a caer en cada reinicio.

El problema no es exclusivo de Windows: en 2024 Red Hat también documentó *kernel panics* en RHEL 9.4 relacionados con el sensor Falcon para Linux.

### Ejercicio

El programa `crowdstrike.c` reproduce el mismo error, pero en **modo usuario**: un intérprete con lugar para 20 campos al que se le pide leer 21. Con `--validar` funciona como versión corregida.

Desde la carpeta `unidad-5`, ejecutar:

```
chmod +x crowdstrike.sh
./crowdstrike.sh
```

El script:
1. Muestra cuántos drivers (módulos) hay cargados en el kernel con `lsmod` y `modinfo`.
2. Ejecuta el intérprete con el error.
3. Muestra que el sistema sigue funcionando (`uptime`) y el registro del error en `dmesg` (pide la contraseña de `sudo`).
4. Ejecuta la versión corregida.

Salida esperada (prueba previa; reemplazar por la del laboratorio):

```
=== 2. El error de CrowdStrike, simulado en MODO USUARIO ===
Interprete: espera 20 campos. La actualizacion usa 21.
  Leyendo campo  1: valor
  ...
  Leyendo campo 20: valor
  Leyendo campo 21: Segmentation fault
Código de salida: 139   (139 = el SO mató al proceso con SIGSEGV)

=== 3. El sistema operativo sigue funcionando ===
crowdstrike[198]: segfault at 7f0042ed6000 ... error 4 in crowdstrike

=== 4. La versión corregida valida la cantidad de campos ===
ERROR: la actualizacion pide 21 campos y solo hay 20. Se rechaza.
El sistema sigue funcionando.
```

Cuando el programa lee el campo 21, el hardware detecta un acceso a memoria prohibida y el kernel termina **solo ese proceso** con la señal `SIGSEGV`. `dmesg` muestra que fue el kernel quien lo frenó y `uptime` confirma que el sistema nunca se cayó.

### Comparación

| Aspecto | CrowdStrike (real) | Nuestro ejercicio |
|---|---|---|
| Qué es | Driver de seguridad Falcon | Programa en C (`crowdstrike.c`) |
| Dónde corre | Modo kernel | Modo usuario |
| El error | Esperaba 20 campos y recibió 21 | Lugar para 20 campos, se piden 21 |
| Quién lo detecta | Nadie: el que falla es el kernel | El kernel detecta el acceso prohibido |
| Consecuencia | Pantalla azul, cae todo Windows | *Segmentation fault*, muere solo el programa |
| ¿El sistema sigue andando? | No, y vuelve a caer en cada reinicio | Sí, lo confirma `uptime` |
| Solución | Validar los datos antes de usarlos | Versión `--validar`: rechaza la actualización |

Relación con el cuestionario: la pregunta 17 (¿los drivers forman parte del kernel?) explica por qué el error fue tan grave, y la pregunta 13 (manejo de errores de E/S) explica la solución.

## Conclusión para el informe

Los dispositivos de bloque permiten acceder a cualquier bloque por su número; los de carácter entregan un flujo de bytes. El número mayor vincula cada archivo de `/dev` con su driver, que corre dentro del kernel. El disco transfiere los datos por DMA y avisa con una interrupción al terminar, sin ocupar a la CPU durante la copia. El búfer agrupa los datos para reducir la cantidad de syscalls.

El caso CrowdStrike muestra por qué importa que los drivers estén dentro del kernel: el mismo error, leer un dato que no existe, en modo usuario mata solo al programa, y en modo kernel tira abajo todo el sistema. Por eso los drivers tienen que validar todos los datos que reciben antes de usarlos.

## Fuentes

- [CrowdStrike – Root Cause Analysis, Channel File 291](https://crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf)
- [The Hacker News – CrowdStrike reveals root cause](https://thehackernews.com/2024/08/crowdstrike-reveals-root-cause-of.html)
- [The Register – Falcon también causó caídas en Linux](https://www.theregister.com/2024/07/21/crowdstrike_linux_crashes_restoration_tools/)
- [Red Hat – Kernel panic con falcon-sensor en RHEL 9.4](https://access.redhat.com/solutions/7068083)

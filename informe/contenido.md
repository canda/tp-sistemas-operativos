# Unidad 1 | Llamadas al sistema
## Problema y objetivo
Una aplicación necesita mostrar un mensaje en la terminal. Se busca explicar cómo el pedido de escritura llega al sistema operativo y observar sus argumentos y su resultado, en lugar de limitarse a ver el texto final.
## Fundamento teórico
Un programa ejecutado en modo usuario no controla directamente los dispositivos. La interfaz de llamadas al sistema permite solicitar servicios al kernel. En este ejercicio, write recibe un descriptor de archivo, una dirección de memoria y una cantidad de bytes. El descriptor 1 identifica la salida estándar. El wrapper de libc prepara la transición al kernel y devuelve el resultado de la operación.
## Implementación y reproducción
unidad-1.c solicita escribir 25 bytes: el mensaje Hola Sistemas Operativos seguido de un salto de línea. El script vigente compila con gcc -O0 -static y luego usa objdump -d para desensamblar el ejecutable. El enlazado estático requiere que las bibliotecas estáticas correspondientes estén disponibles en el laboratorio.
```bash
cd unidad-1
bash compilar.sh
strace -e trace=write ./unidad-1
```
La traza esperada es write(1, "Hola Sistemas Operativos\n", 25) = 25. El retorno expresa los bytes escritos. El programa es mínimo: no comprueba errores ni escrituras parciales.
## Resultados
La primera captura muestra ensamblador x86-64 generado por GCC y una llamada a write. La segunda muestra la traza de una escritura de 25 bytes y finalización con código 0. Ambas provienen de la consola Red Hat.
El ensamblador permite identificar cómo se preparan los argumentos y cómo se llama a write. Puede obtenerse desde el código C con gcc -S o mediante el desensamblado del ejecutable con objdump -d. La primera captura ilustra el primer procedimiento; el script incluido en el anexo utiliza el segundo.
## Conclusión
La traza de strace permite relacionar una instrucción del programa con un servicio concreto del kernel. El proceso solicita la escritura desde modo usuario y recibe como resultado la cantidad de bytes escritos.

# Evidencia de la Unidad 1
![Figura 1. Compilación y listado ensamblador en Red Hat. Fuente: unidad-1/Evidencia U1.png.](unidad-1/Evidencia U1.png)
![Figura 2. Traza de write: solicitud de 25 bytes, retorno 25 y salida con código 0. Fuente: unidad-1/Evidencia U1 - 2.png.](unidad-1/Evidencia U1 - 2.png)

# Unidad 2 | Paralelismo y pseudoparalelismo
## Problema y objetivo
Una computadora debe completar diez tareas independientes. Cada una calcula la suma de los números de 1 a 1.000.000.000. Se compara el tiempo total cuando las tareas se ejecutan una por una, concurrentemente en una CPU lógica o concurrentemente con acceso a todas las CPU permitidas.
## Fundamento teórico
La concurrencia permite mantener varios procesos en progreso. En una única CPU lógica, el planificador alterna su ejecución: esto produce pseudoparalelismo. Con varias CPU disponibles puede haber ejecución simultánea. El tiempo real depende también de las cuotas, la carga y la configuración de la máquina virtual.
## Implementación
El programa C ejecuta la suma con unsigned long long e imprime 500000000500000000. El script compila sin optimizaciones, obtiene la afinidad permitida mediante taskset y toma la primera CPU de esa lista para las dos primeras modalidades. Cada modalidad ejecuta exactamente diez veces el mismo programa.
La modalidad secuencial espera cada proceso antes de iniciar el siguiente. Las otras dos usan & para iniciar procesos en segundo plano y wait para esperar cada PID. Si alguno falla, el script interrumpe el reporte. Con una sola CPU permitida se omite la modalidad paralela.
```bash
cd unidad-2
bash unidad-2.sh
```
El script comprueba gcc, taskset, date y awk; instala los paquetes faltantes con dnf. La medición con date +%s%N incluye el inicio, cálculo, impresión y espera de procesos, pero no la compilación. El cociente entre tiempo secuencial y paralelo se informa como aceleración.
## Análisis de las modalidades
La suma debe producir el mismo resultado numérico en las diez tareas de cada modalidad: 500000000500000000. La pseudoparalela no debería aportar una mejora sustancial para este trabajo de CPU sobre una sola CPU lógica.
El reporte del script presenta los tiempos de cada modalidad y calcula la aceleración como tiempo secuencial dividido por tiempo paralelo. Estos valores dependen de los recursos disponibles: varias CPU lógicas pueden compartir núcleos físicos o estar sujetas a cuotas de uso.
## Conclusión
El ejercicio mantiene constante la cantidad de trabajo y cambia la forma de planificarlo. Permite separar concurrencia de paralelismo y discutir por qué iniciar más procesos no garantiza reducir el tiempo total.

# Evidencia de la Unidad 2 | Ejecución
![Figura 3. CPU permitidas y resultados de las tareas secuenciales y concurrentes. Fuente: unidad-2/unidad-2-evidencia-1.jpeg.](unidad-2/unidad-2-evidencia-1.jpeg)
La ejecución dispone de cuatro CPU lógicas, numeradas de 0 a 3. La terminal muestra el mismo resultado numérico en las tareas: 500000000500000000. El script mantiene esa carga de trabajo y cambia la afinidad y la concurrencia entre modalidades.

# Evidencia de la Unidad 2 | Tiempos
![Figura 4. Reporte del tiempo total de diez tareas por modalidad. Fuente: unidad-2/unidad-2-evidencia-2.jpeg.](unidad-2/unidad-2-evidencia-2.jpeg)
## Resultados de la ejecución
- Secuencial: 28,375 segundos.
- Pseudoparalela: 28,168 segundos.
- Paralela: 7,428 segundos.
- Aceleración paralela respecto de la secuencial: 3,82 veces.
Los tiempos secuencial y pseudoparalelo son similares, mientras que el acceso concurrente a las cuatro CPU permitidas reduce el tiempo total. La aceleración se calcula como 28,375 / 7,428 y corresponde a esta ejecución concreta.

# Unidad 3 | Compilación, carga y memoria
## Problema y objetivo
Se plantea el escenario hipotético de un servicio backend que sufre un pico repentino de consumo de memoria. La aplicación necesita reservar 100 MiB y acceder de manera espaciada a esa región. Se estudia cómo se construye el ejecutable, cómo se monitorea su ejecución en segundo plano y cómo se evidencian sus accesos físicos a la memoria virtual utilizando herramientas nativas del sistema operativo.
## Fundamento teórico
La construcción comprende preprocesamiento, compilación, ensamblado y enlace. Al ejecutar el programa, el sistema crea su espacio de direcciones y prepara la imagen del proceso. Las direcciones virtuales utilizadas por el código se traducen mediante las estructuras de memoria y la MMU. La reserva lógica de memoria (demand paging) y la disponibilidad de páginas físicas no son necesariamente el mismo evento.
## Implementación
compilar.sh verifica GCC, compila paginacion.c con -Wall -Wextra -O0 y presenta el contexto de la simulación. Para permitir el monitoreo, el script ejecuta el binario en segundo plano (`&`) y captura su PID. El programa solicita 104.857.600 bytes con malloc e introduce pausas estratégicas (usando `sleep`). Luego escribe un byte cada 4096 posiciones, produciendo 25.600 escrituras separadas. 
Mientras el programa retiene la memoria, el script utiliza comandos de la consola de Red Hat (`free`, `ps`, `vmstat`) para auditar el proceso.
```bash
cd unidad-3
bash compilar.sh
```
## Relación con la memoria virtual
Con páginas de 4096 bytes, el recorrido relaciona cada salto del programa con la granularidad de la paginación. Las escrituras fuerzan fallos de página (page faults), obligando al sistema a asignar marcos físicos para el bloque reservado. 
Las herramientas de monitoreo evidencian este proceso: `ps` permite contrastar la memoria virtual total solicitada por el proceso (VSZ) con la memoria física residente que realmente ocupó en la RAM (RSS). Por su parte, `vmstat 1 3` y `free -h` reflejan la caída temporal de la memoria disponible a nivel global y su posterior recuperación al finalizar el programa.
La compilación sin -static utiliza el enlace habitual del entorno, normalmente dinámico en Red Hat. Así, el ejercicio conecta la generación del ejecutable con su carga y el acceso a direcciones virtuales durante la ejecución.
## Conclusión
La reserva con malloc, el recorrido del bloque y su liberación permiten seguir el uso de memoria desde el programa. El sistema operativo administra el espacio de direcciones y su respaldo físico, mientras que las herramientas de consola demuestran cómo la aplicación trabaja con direcciones virtuales que se traducen en consumo real de RAM, el cual es recuperado instantáneamente por el sistema al liberar la memoria.

# Evidencia de la Unidad 3
![Figura X. Monitoreo de memoria en Red Hat: ejecución en segundo plano, contraste de memoria VSZ/RSS y estadísticas en tiempo real. Fuente: unidad-3/Captura de pantalla.png.](unidad-3/Captura de pantalla.png)

# Unidad 4 | Almacenamiento y sistema de archivos
## Problema y objetivo
Un laboratorio dispone de un disco virtual adicional destinado a datos. Se propone crear una partición, formatearla con XFS y montar su contenido en /mnt/datos de forma persistente.
## Fundamento teórico
Una partición delimita una región del dispositivo. El formateo crea las estructuras del sistema de archivos. El montaje incorpora ese sistema de archivos al árbol de directorios. Una entrada en /etc/fstab permite declarar su montaje y el UUID identifica el sistema de archivos independientemente del nombre del dispositivo.
## Implementación
unidad-4.sh utiliza /dev/vdb como disco y /dev/vdb1 como partición. Envía a fdisk una secuencia de respuestas para crear una partición primaria, ejecuta mkfs.xfs -f, crea /mnt/datos y obtiene el UUID con blkid. Después actualiza la entrada correspondiente en /etc/fstab y ejecuta mount -a y df -h.
El procedimiento está planteado para un disco virtual de laboratorio vacío, identificado previamente y administrado con permisos de root. La secuencia de fdisk supone una tabla de particiones compatible con la creación de una partición primaria. El formateo reemplaza el sistema de archivos del dispositivo seleccionado.
```bash
cd unidad-4
sudo bash unidad-4.sh
```
## Partición, formato y montaje
fdisk define la partición que se utilizará para almacenar los datos. mkfs.xfs crea sus estructuras de sistema de archivos. mkdir -p prepara el directorio de acceso y mount incorpora el volumen al árbol de directorios. Son pasos diferentes: crear una partición no equivale a formatearla, y formatearla no implica que ya esté montada.
La entrada de /etc/fstab usa UUID para identificar el sistema de archivos y /mnt/datos como destino. De esta forma, la configuración de montaje no depende exclusivamente de que el dispositivo mantenga el nombre /dev/vdb1.
## Comprobación del montaje
lsblk permite consultar los dispositivos y particiones; blkid muestra el UUID; findmnt /mnt/datos y df -h permiten comprobar el montaje. Estas consultas verifican el estado del sistema independientemente de los mensajes que imprima el script.
El archivo C del anexo es un lanzador mediante system y utiliza el nombre configurar_disco.sh. El procedimiento de este ejercicio invoca directamente unidad-4.sh con Bash, como se indica arriba.
## Conclusión
El ejercicio integra particionado, formato y montaje persistente. El uso de UUID vincula la configuración con el sistema de archivos, mientras que las herramientas de consola permiten consultar cada etapa de la administración del almacenamiento.

# Unidad 5 | Entrada y salida: parte A
## Problema y objetivo
Se necesita identificar dispositivos de bloque y carácter y analizar cuánto cambia el costo de leer un archivo al variar el tamaño del búfer. También se observa el contador de interrupciones antes y después de una escritura de disco.
## Fundamento teórico
Los archivos especiales de /dev permiten acceder a dispositivos. El número mayor identifica su clase o controlador y el menor distingue dispositivos dentro de esa clase. Las lecturas solicitan al kernel transferir datos al proceso. Un búfer mayor permite solicitar más bytes por operación y reducir la cantidad de invocaciones para recorrer el mismo archivo.
## Implementación
El script compila el programa, selecciona el primer disco que coincide con su criterio en lsblk y genera prueba.bin con 2.000.000 de bytes. El programa consulta stat sobre los dispositivos recibidos y recorre el archivo usando búferes de 1, 512, 4096 y 65536 bytes. Mide con CLOCK_MONOTONIC. El script consulta /proc/devices y compara contadores de /proc/interrupts alrededor de una escritura con dd y oflag=direct.
```bash
cd unidad-5
bash ejecutar.sh
```
## Resultados observados
La captura muestra /dev/vda como dispositivo de bloque, mayor 252 y menor 0; /dev/null, /dev/tty y /dev/urandom aparecen como dispositivos de carácter. Los tiempos y conteos visibles se transcriben en la página siguiente.
## Análisis de los resultados
El contador del C aumenta solo cuando read devuelve un valor positivo. No incluye la última invocación que devuelve 0 por fin de archivo. Por eso la columna del programa representa lecturas con datos, no todas las llamadas realizadas. Para un búfer de 1 byte hay 2.000.000 de lecturas positivas y una comprobación final de fin de archivo.
La caché de páginas y el orden fijo de las pruebas influyen en los tiempos: no son una medición aislada de velocidad del disco. El contador de interrupciones agrupa coincidencias de varios controladores y puede incluir actividad ajena al ejercicio. No demuestra por sí mismo el uso de DMA ni una correspondencia de una interrupción por transferencia.
Además, bs=1M y count=100 de dd corresponden a 100 MiB (104.857.600 bytes), aunque el mensaje del script diga 100 MB. El archivo de lectura sí contiene 2 MB decimales.

# Evidencia de la Unidad 5 | Parte A
![Figura 5. Dispositivos, lecturas con distintos búferes e interrupciones en Red Hat. Fuente: unidad-5/Evidencia U5-Parte A.png.](unidad-5/Evidencia U5-Parte A.png)
## Transcripción de la captura
- Búfer de 1 byte: 2.000.000 de lecturas positivas; 0,5975 s.
- Búfer de 512 bytes: 3.907 lecturas positivas; 0,0017 s.
- Búfer de 4096 bytes: 489 lecturas positivas; 0,0006 s.
- Búfer de 65536 bytes: 31 lecturas positivas; 0,0004 s.
- Interrupciones: 327.624 antes, 327.771 después; diferencia de 147.
## Conclusión
La evidencia muestra que agrupar los bytes reduce fuertemente la cantidad de lecturas y el tiempo observado en esta ejecución. La explicación se relaciona con el costo de las operaciones de entrada/salida y el uso de búferes; la magnitud de la mejora no debe generalizarse a todos los equipos o cargas.

# Unidad 5 | Parte B: drivers y fallos
## Problema y relación con la unidad
Un componente interpreta una configuración con veinte campos. Una actualización solicita un campo adicional. El ejercicio analiza qué sucede al acceder a ese campo desde un proceso de usuario y relaciona el resultado con el impacto de un fallo en un componente que se ejecuta dentro del kernel.
## Caso CrowdStrike
El 19 de julio de 2024, una actualización de contenido de Falcon para Windows provocó fallos de sistema. El análisis de CrowdStrike explica la discrepancia entre veinte entradas suministradas al intérprete y el acceso a una entrada número veintiuno. La falta de una comprobación de límites permitió una lectura fuera del arreglo. El caso relaciona la validación de datos con la importancia del contexto de ejecución de los controladores. Fuente: CrowdStrike, análisis de causa raíz del Channel File 291 (2024).
## Implementación de la simulación
crowdstrike.c consulta el tamaño de página con sysconf, reserva dos páginas con mmap y protege la segunda con mprotect y PROT_NONE. Coloca veinte punteros al final de la primera página. De esta manera, el acceso al puntero veintiuno cae en la página protegida. Esta disposición fuerza un fallo de acceso para la demostración; una lectura fuera de límites en un programa cualquiera no siempre produce una caída inmediata.
Con el argumento --validar, el programa rechaza una solicitud mayor que veinte antes de recorrer los campos. La simulación se ejecuta en modo usuario y no carga un driver ni modifica el kernel.
```bash
cd unidad-5
bash crowdstrike.sh
```
El script compila el programa, consulta los módulos con lsmod y modinfo, ejecuta el caso de veintiún campos, muestra su estado de salida y consulta uptime y dmesg. Luego ejecuta la variante con validación.
## Comportamiento de los casos
- ./crowdstrike 20: recorre los veinte campos y termina normalmente.
- ./crowdstrike 21: intenta leer la página protegida; en el entorno Linux previsto se espera SIGSEGV, representada habitualmente por Bash como estado 139.
- ./crowdstrike 21 --validar: rechaza la cantidad solicitada y devuelve estado 1 sin realizar el acceso inválido.
La señal concreta y los registros disponibles dependen del entorno. La consulta de dmesg puede requerir permisos de administración. El código de salida permite distinguir la terminación normal, el rechazo controlado y la terminación por una señal.
## Conclusión
En modo usuario, el sistema puede terminar el proceso que realiza el acceso inválido y continuar atendiendo otros procesos. Un fallo dentro del kernel puede comprometer al sistema completo, como ocurrió en el caso analizado. La demostración representa el control de límites y el aislamiento de procesos; no reproduce el componente Falcon ni una caída real del kernel.

# Unidad 6 | Seguridad y exposición de memoria
## Problema y objetivo
Una aplicación permite consultar el nombre de usuario y prohíbe consultar una contraseña ficticia. El solicitante elige el campo y la longitud. Se demuestra que bloquear el acceso directo al campo privado no alcanza cuando una longitud excesiva permite incluir sus bytes en otra respuesta.
## Fundamento teórico
La protección de memoria del sistema operativo separa espacios de procesos, pero no interpreta las reglas de confidencialidad de cada aplicación. Si ambos campos están en memoria accesible para el proceso, es responsabilidad del programa limitar qué bytes puede entregar.
## Implementación
El array char datos[2][16] contiene usuario y clave123, con terminadores y relleno de ceros. Son datos de demostración. El programa rechaza el campo 1, acepta el campo 0 y permite longitudes de hasta sizeof(datos), es decir, 32 bytes. write recibe la dirección del array completo y la longitud solicitada. Como no interpreta cadenas, no se detiene ante los bytes nulos.
```bash
cd unidad-6
bash unidad-6.sh
# Una vez compilado:
printf '0\n32\n' | ./unidad-6 | od -An -tx1c
strace -e trace=write ./unidad-6
```
## Casos y corrección propuesta
- Campo 1: acceso rechazado antes de pedir longitud.
- Campo 0 y longitud 16: consulta de la primera fila completa.
- Campo 0 y longitud 32: respuesta con ambos campos.
- Campo 0 y longitud 33: rechazo por superar el array completo.
La corrección propuesta es comparar con sizeof(datos[0]), que limita el acceso a los 16 bytes del campo permitido. El código del repositorio conserva intencionalmente la validación vulnerable. De esta manera, una solicitud de 32 bytes se rechazaría antes de realizar la escritura.
## Relación con Heartbleed
OWASP describe Heartbleed (CVE-2014-0160) como una falta de validación de límites antes de copiar datos, que permitió exponer memoria de OpenSSL. La analogía es devolver más información que la autorizada por confiar en una longitud. Este ejercicio permanece dentro del array de 32 bytes; no reproduce TLS, no lee otros procesos ni accede fuera del objeto completo. Fuente: OWASP, Heartbleed Bug, consultada el 02/11/2026.

# Evidencia de la Unidad 6
![Figura 6. Rechazo del campo privado, consulta normal y exposición mediante longitud 32. Fuente: unidad-6/Evidencia U6.png.](unidad-6/Evidencia U6.png)
## Lectura de la evidencia
La imagen original registra la instalación de GCC. El detalle reproducido muestra la compilación manual con gcc unidad-6.c y tres ejecuciones de ./a.out. Primero se rechaza el campo 1. Después se solicita el campo 0 con longitud 8 y se ve usuario. Finalmente, con longitud 32 se observa usuarioclave123; los ceros de relleno no son visibles en la terminal.
Los tres casos permiten comparar el control sobre el campo solicitado con el control sobre la longitud: el acceso directo se rechaza, pero una consulta al campo autorizado puede abarcar también el dato privado.
## Conclusión
La confidencialidad depende tanto del campo autorizado como de la extensión del acceso. Un control correcto sobre el selector puede quedar anulado por otro control demasiado amplio sobre la longitud. La operación puede ser válida para el kernel y, al mismo tiempo, violar la regla de seguridad de la aplicación.

# Conclusiones generales
Los seis ejercicios relacionan los conceptos de Sistemas Operativos con programas C y herramientas de consola de Red Hat. Las llamadas al sistema permiten solicitar servicios al kernel; la planificación determina cómo se distribuye el tiempo de CPU; y la memoria virtual ofrece a cada proceso un espacio de direcciones sobre el que trabaja la aplicación.
La administración de almacenamiento conecta dispositivos, particiones, sistemas de archivos y puntos de montaje. En entrada y salida, el tamaño del búfer influye sobre la cantidad de operaciones necesarias para procesar los mismos datos. El caso de los controladores permite comparar las consecuencias de un fallo según el modo de ejecución. Finalmente, el ejercicio de seguridad muestra que la protección del sistema operativo debe complementarse con controles adecuados dentro del programa.
Bash permite organizar estos procedimientos: compilar, ejecutar procesos, esperar su finalización, medir tiempos y consultar el estado del sistema. C permite observar de forma directa operaciones de memoria y entrada/salida. Su uso conjunto vincula la explicación teórica con el funcionamiento de cada ejercicio.
## Referencias
- UADE. Sistemas Operativos: consigna del Trabajo Práctico Obligatorio y material de la asignatura. Segundo cuatrimestre de 2026.
- Código fuente y capturas de los ejercicios incluidos en este trabajo.
- OWASP Foundation. Heartbleed Bug. https://community.owasp.org/vulnerabilities/Heartbleed_Bug (consulta: 02/11/2026).
- CrowdStrike. Executive Summary: Root Cause Analysis - Channel File 291, 6 de agosto de 2024. https://www.crowdstrike.com/wp-content/uploads/2024/08/Executive-Summary_Root-Cause-Analysis_Channel-File-291.pdf (consulta: 02/11/2026).

Unidad 1 – Llamadas al sistema

Objetivo: observar cómo un programa solicita al kernel una escritura mediante una llamada al sistema.

Entorno: consola del laboratorio Red Hat del curso.

1. El programa `unidad-1.c` llama al wrapper `write` de libc, declarado en `<unistd.h>`, para solicitar la syscall `write`. Escribe `Hola Sistemas Operativos` seguido de un salto de línea: 25 bytes. El descriptor 1 corresponde a la salida estándar.

2. Desde la carpeta `unidad-1`, compilar el programa y generar su ensamblador:

```bash
./compilar.sh
```

El script usa `gcc -O0` para crear el ejecutable y `gcc -S -O0` para generar ensamblador desde el código C. Este segundo paso no desensambla el ejecutable. No hace falta enlazado estático para observar las llamadas al sistema.

3. Confirmar la escritura durante la ejecución:

```bash
strace -e trace=write ./unidad-1
```

La traza esperada de la escritura es:

```text
write(1, "Hola Sistemas Operativos\n", 25) = 25
```

El retorno 25 indica que se escribieron los 25 bytes solicitados.

Conclusión para el informe: el programa llama al wrapper `write` en modo usuario; este solicita la operación al kernel mediante una instrucción de entrada al sistema dependiente de la arquitectura. El kernel atiende la solicitud y devuelve el control y el resultado al programa a través del wrapper.

El ensamblador generado muestra la preparación de los argumentos y la llamada al wrapper. La instrucción que entra al kernel está dentro de libc, no en el ensamblador de `main`. La sintaxis y las instrucciones dependen de la arquitectura del laboratorio.

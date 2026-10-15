# Unidad 3 – Compilación, enlace y carga

**Objetivo:** entender cómo `compilar.sh` convierte `paginacion.c` en un ejecutable y lo lleva a memoria, relacionando cada paso con los temas de la Unidad 3.

**Entorno:** consola Linux de la familia Red Hat (el script usa `dnf`).

1. El script se da permiso de ejecución con `chmod +x "$0"` y verifica si `gcc` está instalado. Si no lo está, lo instala con `sudo dnf install -y gcc`.
2. Compila el programa con `gcc -Wall -Wextra -O0 paginacion.c -o paginacion`. Las opciones `-Wall` y `-Wextra` activan advertencias, `-O0` desactiva las optimizaciones y `-o` define el nombre del ejecutable. Este único comando recorre las fases vistas en la unidad (págs. 11-14):
   - Preprocesamiento: expande los `#include` y las macros.
   - Compilación: verifica la sintaxis y traduce a ensamblador.
   - Ensamblado: genera el código objeto, con referencias externas sin resolver.
   - Enlace: une el código objeto con las bibliotecas y produce el módulo de carga (el ejecutable).
3. Si `gcc` devuelve un código distinto de 0, el script muestra un error y termina con `exit 1`. Así no se intenta ejecutar un binario que no se generó.
4. Si todo salió bien, da permiso de ejecución al binario con `chmod +x paginacion` y lo ejecuta:
```bash
./compilar.sh
```

Al ejecutar `./paginacion` interviene el cargador del sistema operativo (págs. 19-24): toma el ejecutable del disco, lo coloca en memoria principal y crea la imagen del proceso con su espacio de direcciones. Una vez en ejecución, el programa usa direcciones lógicas (virtuales) y la MMU las traduce a direcciones físicas (págs. 26-28).

**Conclusión para el informe:** `compilar.sh` automatiza el ciclo completo de preprocesamiento, compilación, ensamblado, enlace y carga. Sin `-static`, `gcc` enlaza de forma dinámica con las bibliotecas compartidas del sistema (págs. 15-18), de modo que el ejecutable no incluye su propia copia de la biblioteca estándar. El control con el código de salida evita ejecutar un programa que no compiló.

**Nota:** no revisé el contenido de `paginacion.c`, por lo que este documento describe solo el script y no lo que hace el programa.
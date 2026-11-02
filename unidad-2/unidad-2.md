# Unidad 2 – Paralelismo y pseudoparalelismo

Una computadora debe realizar cuatro tareas independientes. Cada tarea suma los números de 1 a 1.000.000.000. Se compara el tiempo total para completar las cuatro tareas de tres maneras:

- Secuencial: un proceso después del otro, sobre una misma CPU lógica.
- Pseudoparalela: cuatro procesos concurrentes sobre esa misma CPU lógica. El SO alterna su ejecución.
- Paralela: cuatro procesos concurrentes con acceso a todas las CPU permitidas. El SO puede ejecutarlos simultáneamente.

En la consola del laboratorio Red Hat, desde esta carpeta:

```bash
bash unidad-2.sh
```

Si faltan herramientas, el script instala automáticamente los paquetes necesarios con `dnf install -y`. Usa `sudo` cuando no se ejecuta como root; requiere permisos de administración y acceso a los repositorios. Si la instalación falla, el script se detiene antes de compilar o medir.

El script compila con GCC sin optimizaciones, ejecuta las modalidades una después de otra y muestra un reporte en segundos. Cada proceso debe imprimir `Resultado: 500000000500000000`. El programa C sólo calcula e imprime; Bash organiza y mide las ejecuciones. `&` lanza procesos en segundo plano, `wait` espera su finalización y `taskset` restringe las CPU donde pueden ejecutarse.

La medición incluye iniciar los procesos, calcular, imprimir y esperar a que terminen; excluye la compilación. Se realiza la misma cantidad de trabajo en las tres modalidades. La pseudoparalela no debería acelerar sustancialmente este trabajo de CPU respecto de la secuencial; la paralela puede reducir su tiempo si existen recursos disponibles.

Si sólo hay una CPU lógica permitida, el script omite la prueba paralela. Varias CPU lógicas no garantizan núcleos físicos exclusivos: el hardware, las cuotas de CPU y la carga de la máquina virtual pueden limitar la aceleración. Repetir el script para observar la variación y guardar capturas del reporte real del laboratorio. No hay tiempos predeterminados ni una aceleración garantizada.

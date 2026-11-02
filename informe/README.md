# Informe del Trabajo Práctico Obligatorio

- `reporte-sistemas-operativos.pdf`: informe para lectura y entrega, con carátula, seis unidades, cuatro capturas y código completo.
- `contenido.md`: texto editable del cuerpo del informe. Las imágenes se resuelven contra el commit de referencia.
- `metadatos.json`: integrantes, docente, fecha y commit relevado.
- `generar.py`: generador del PDF con ReportLab.
- `manifiesto.json`: trazabilidad del commit, insumos y PDF generado mediante SHA-256.

## Actualizar

1. Completar nombres y legajos en `metadatos.json`.
2. Para incorporar avances, comparar el commit anterior con el nuevo: `git diff COMMIT_ANTERIOR COMMIT_NUEVO -- unidad-* consignas-tpo.md`.
3. Revisar `contenido.md`, especialmente afirmaciones, resultados y pendientes. Agregar nuevas capturas al repositorio y citarlas con `![Descripción](unidad-N/archivo.png)`.
4. Actualizar `commit`, `commit_titulo`, `commit_fecha`, `rama` y la fecha del informe en `metadatos.json`. El generador NO actualiza automáticamente las conclusiones ni toma cambios sin commit.
5. Desde la raíz del repositorio, ejecutar `python3 informe/generar.py` con ReportLab instalado. El generador utiliza fuentes Arial y Courier New del sistema macOS; en otro sistema se deben adaptar esas rutas.
6. Revisar visualmente el PDF. El nuevo manifiesto contiene las huellas de los insumos y del resultado.

El código y las imágenes se leen con `git show` desde el commit configurado. No se ejecutan los ejercicios. El anexo conserva sus inconsistencias para documentar fielmente la revisión. El texto y los metadatos se leen desde los archivos editables de esta carpeta.

Docente y datos de la materia verificados en `/Users/javiercandalaft/projects/canda/uade/2026-h2/sistemas-operativos/material-teams/cronograma.md`. Las capturas existentes son evidencia histórica; deben revalidarse cuando cambie el comportamiento documentado.

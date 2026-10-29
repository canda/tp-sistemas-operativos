# Unidad 6 – Seguridad y exposición de memoria

**Objetivo:** demostrar cómo una validación incorrecta de longitud permite revelar información privada de la memoria de un programa.

**Entorno:** consola del laboratorio Red Hat del curso.

**Problema hipotético:** una aplicación permite consultar un nombre de usuario, pero prohíbe consultar su contraseña. El usuario puede indicar qué campo quiere leer y cuántos bytes quiere recibir. Aunque la aplicación controla el campo elegido, una longitud excesiva permite obtener también la contraseña.

1. El programa `unidad-6.c` guarda dos textos ficticios en `char datos[2][16]`: un array bidimensional de caracteres con dos filas de 16 bytes, almacenadas consecutivamente en memoria.
   - `datos[0]` contiene `usuario` y ceros de relleno.
   - `datos[1]` contiene `clave123` y ceros de relleno.
   - Cada fila ocupa 16 bytes y el array completo ocupa 32 bytes. Cada fila admite un texto de hasta 15 caracteres más el terminador `\0`.

2. Desde la carpeta `unidad-6`, compilar y ejecutar con el script:

```bash
bash unidad-6.sh
```

El script se ubica en su propia carpeta, por lo que también se puede invocar pasando su ruta desde otro directorio. Verifica si existe `gcc` y, si falta, intenta instalarlo con `sudo dnf install -y gcc` (requiere permisos de administración y acceso a los repositorios). Después compila con `-Wall -Wextra -O0` y ejecuta el programa. `set -e` detiene el script si falla la instalación o compilación, evitando ejecutar un binario anterior. Al invocarlo con `bash`, no hace falta darle permiso de ejecución.

3. Repetir `./unidad-6` después de la primera compilación, o volver a ejecutar `bash unidad-6.sh`, para probar los siguientes casos:

| Campo | Longitud | Resultado esperado |
|---|---:|---|
| `1` (contraseña) | No se solicita | Muestra que no hay permiso y termina. |
| `0` (usuario) | `16` | Devuelve el usuario y los ceros de relleno de su fila. |
| `0` (usuario) | `32` | Devuelve ambas filas: expone también la contraseña. |
| `0` (usuario) | `33` | Rechaza la longitud porque supera el tamaño del array completo. |

En la terminal, los ceros de relleno normalmente no se ven. Para observar los bytes de la respuesta, ejecutar:

```bash
printf '0\n32\n' | ./unidad-6 | od -An -tx1c
```

La salida incluye los mensajes del programa y la respuesta. Los bytes `00` corresponden al relleno entre los textos y al final de cada fila.

4. Observar la llamada al sistema en Red Hat, después de compilar. Si `strace` no está instalado, instalarlo con `sudo dnf install -y strace`; el script solo verifica GCC.

```bash
strace -e trace=write ./unidad-6
```

Ingresar campo `0` y longitud `32`. Además de las escrituras de los mensajes, se espera una llamada a `write` con 32 bytes que incluya ambos textos. Guardar capturas del acceso rechazado, la consulta normal y la filtración con su traza.

5. La falla está en esta validación:

```c
if (longitud < 1 || longitud > (int) sizeof(datos)) {
```

El límite es el tamaño del array completo, aunque solo está autorizado el primer campo. Luego, `write(STDOUT_FILENO, &datos, (size_t) longitud)` entrega esa cantidad de bytes a la salida estándar. `write` no interpreta strings ni se detiene ante un `\0`.

La corrección propuesta es limitar la lectura al tamaño del campo autorizado:

```c
if (longitud < 1 || longitud > (int) sizeof(datos[0])) {
```

Con ese cambio, una longitud de 32 debe rechazarse. El archivo original conserva la falla intencional para la demostración.

**Relación con Sistemas Operativos:** el programa llama al wrapper `write` de libc para solicitar al kernel que escriba bytes de su memoria. El proceso tiene acceso a las dos filas, por lo que la protección de memoria del SO no impide esta operación. El kernel no conoce la regla de la aplicación que considera privada la contraseña. La autorización del campo y la validación de la longitud son responsabilidad del programa.

La demostración permanece dentro de los 32 bytes del array: no lee memoria de otros procesos ni fuera del objeto completo. Simula una filtración por lectura excesiva respecto del campo permitido, sin depender de que variables independientes queden contiguas en memoria. El dato afectado pierde su confidencialidad aunque no sea modificado.

**Caso relacionado: Heartbleed.** En abril de 2014 se hizo pública la vulnerabilidad CVE-2014-0160 de OpenSSL. En el procesamiento de mensajes heartbeat faltaba comprobar la longitud declarada antes de copiar datos con `memcpy`. Una solicitud podía provocar que se devolvieran datos adicionales de la memoria del proceso, incluyendo información sensible. OWASP lo clasifica como *buffer over-read* (CWE-126).

La similitud con el ejercicio es confiar en una longitud que permite devolver más información de la prevista. La diferencia es que Heartbleed podía leer más allá del buffer del mensaje; este programa limita la lectura al array completo y prepara dos campos contiguos para mostrar el mecanismo de forma controlada. No reproduce OpenSSL ni el protocolo TLS.

Fuente: [OWASP – Heartbleed Bug](https://community.owasp.org/vulnerabilities/Heartbleed_Bug).

**Conclusión para el informe:** bloquear la consulta directa de un campo privado no alcanza si otra operación permite leer los mismos bytes. Es necesario validar tanto el recurso autorizado como la extensión del acceso. La protección del SO entre procesos no reemplaza los controles de confidencialidad dentro de una aplicación.

#include <stdio.h>
#include <unistd.h>

int main(void) {
    char datos[2][16] = {"usuario", "clave123"};
    int campo, longitud;

    printf("Campo a consultar (0: usuario, 1: contraseña): ");
    if (scanf("%d", &campo) != 1) {
        return 1;
    }

    if (campo == 1) {
        printf("Error: no tenés permiso para leer la contraseña.\n");
        return 1;
    }

    if (campo != 0) {
        printf("Error: campo inexistente.\n");
        return 1;
    }

    printf("Longitud a leer: ");
    if (scanf("%d", &longitud) != 1) {
        return 1;
    }

    // Evita salir del bloque completo, pero no protege el campo privado.
    if (longitud < 1 || longitud > (int) sizeof(datos)) {
        printf("Error: longitud inválida.\n");
        return 1;
    }

    printf("Resultado: ");
    fflush(stdout);

    // Falla: el campo está autorizado, pero la longitud puede abarcar ambos.
    write(STDOUT_FILENO, &datos, (size_t) longitud);
    write(STDOUT_FILENO, "\n", 1);

    return 0;
}

/*
 * Unidad 5 - Caso real: CrowdStrike (19 de julio de 2024)
 *
 * Simula el error del "Content Interpreter" de CrowdStrike Falcon:
 * el interprete esperaba 20 campos, pero la actualizacion usaba un campo 21.
 * Al leer el campo 21 accede fuera del arreglo (out-of-bounds read).
 *
 * Aca corre en MODO USUARIO: el SO mata solo a este proceso.
 * En CrowdStrike corria en MODO KERNEL (era un driver): cayo todo Windows.
 *
 * Uso:  ./crowdstrike 21              -> version con el error
 *       ./crowdstrike 21 --validar    -> version corregida
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define CAMPOS 20   /* el interprete fue programado para 20 campos */

int main(int argc, char *argv[]) {
    int pedido = (argc > 1) ? atoi(argv[1]) : 21;
    int validar = (argc > 2 && strcmp(argv[2], "--validar") == 0);

    /* Se reserva una pagina para los 20 campos y se protege la pagina siguiente,
       asi leer el campo 21 siempre cae en memoria prohibida (igual que en el caso real) */
    long pag = sysconf(_SC_PAGESIZE);
    char *mem = mmap(NULL, 2 * pag, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    mprotect(mem + pag, pag, PROT_NONE);
    const char **campos = (const char **)(mem + pag - CAMPOS * sizeof(char *));

    for (int i = 0; i < CAMPOS; i++) campos[i] = "valor";

    printf("Interprete: espera %d campos. La actualizacion usa %d.\n", CAMPOS, pedido);

    if (validar && pedido > CAMPOS) {
        printf("ERROR: la actualizacion pide %d campos y solo hay %d. Se rechaza.\n", pedido, CAMPOS);
        printf("El sistema sigue funcionando.\n");
        return 1;
    }

    for (int i = 0; i < pedido; i++) {
        printf("  Leyendo campo %2d: ", i + 1);
        fflush(stdout);
        printf("%s\n", campos[i]);   /* campos[20] esta fuera del arreglo */
    }
    printf("Actualizacion aplicada.\n");
    return 0;
}

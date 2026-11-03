#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    size_t total = 1024 * 1024 * 100; // 100 MiB
    
    printf("[Programa C] PID del proceso: %d\n", getpid());
    printf("[Programa C] Esperando 3 segundos antes de asignar memoria...\n");
    sleep(3);

    char *buf = malloc(total);
    if (buf == NULL)
    {
        perror("malloc");
        return 1;
    }

    // Forzar la asignación real de marcos de página en la RAM
    for (size_t i = 0; i < total; i += 4096)
    {
        buf[i] = 1;
    }

    printf("[Programa C] 100 MiB paginados. Manteniendo memoria ocupada por 10 segundos...\n");
    sleep(10);

    free(buf);
    printf("[Programa C] Memoria liberada. Fin.\n");
    return 0;
}
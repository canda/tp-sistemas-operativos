#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    size_t total = 1024 * 1024 * 100; // 100 MiB

    char *buf = malloc(total);
    if (buf == NULL)
    {
        perror("malloc");
        return 1;
    }

    for (size_t i = 0; i < total; i += 4096)
    {
        buf[i] = 1;
    }

    printf("Se recorrieron páginas de memoria de 4096 bytes.\n");

    free(buf);
    return 0;
}
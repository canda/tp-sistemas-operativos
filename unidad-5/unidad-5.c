#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <time.h>
#include <unistd.h>

static double ahora(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(int argc, char *argv[]) {
    /* Parte 1: tipo de dispositivo y numeros mayor/menor */
    for (int i = 2; i < argc; i++) {
        struct stat st;
        if (stat(argv[i], &st) < 0) { perror(argv[i]); continue; }
        printf("%-14s %-9s mayor=%-3u menor=%u\n", argv[i],
               S_ISBLK(st.st_mode) ? "BLOQUE" : S_ISCHR(st.st_mode) ? "CARACTER" : "ARCHIVO",
               major(st.st_rdev), minor(st.st_rdev));
    }

    /* Parte 2: leer el mismo archivo con distintos tamanos de bufer */
    printf("\nBufer(B)  Llamadas read()  Tiempo\n");
    int tams[] = {1, 512, 4096, 65536};
    for (int t = 0; t < 4; t++) {
        char *buf = malloc(tams[t]);
        int fd = open(argv[1], O_RDONLY);
        long llamadas = 0;
        double t0 = ahora();
        while (read(fd, buf, tams[t]) > 0) llamadas++;
        printf("%-9d %-16ld %.4f s\n", tams[t], llamadas, ahora() - t0);
        close(fd);
        free(buf);
    }
    return 0;
}

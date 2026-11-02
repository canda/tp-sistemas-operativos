#include <stdio.h>

int main(void)
{
    unsigned long long suma = 0;

    for (unsigned long long i = 1; i <= 1000000000ULL; i++) {
        suma += i;
    }

    printf("Resultado: %llu\n", suma);
    return 0;
}

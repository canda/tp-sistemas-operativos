#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("Iniciando la configuración del disco de la Unidad 4...\n");

    // Ejecuta el script de bash automatizado
    int ret = system("./configurar_disco.sh");
    
    if (ret == -1) {
        perror("Error al ejecutar el script de configuración");
        return 1;
    }

    printf("Configuración de almacenamiento finalizada con éxito.\n");
    return 0;
}
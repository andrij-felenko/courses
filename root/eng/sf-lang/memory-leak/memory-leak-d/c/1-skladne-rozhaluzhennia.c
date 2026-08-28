#include <stdio.h>
#include <stdlib.h>

int parse_config(const char *filename) {
    char *header = (char *)malloc(128);
    char *body = (char *)malloc(1024);
    if (!header || !body) {
        /* Якщо body не виділився, header витікає! */
        return -1; 
    }

    FILE *f = fopen(filename, "r");
    if (!f) {
        /* ПОМИЛКА: забули free(header) та free(body) */
        return -2; 
    }

    if (fread(header, 1, 128, f) < 128) {
        fclose(f);
        /* ПОМИЛКА: ще один витік обох буферів */
        return -3; 
    }

    fclose(f);
    free(body);
    free(header);
    return 0;
}

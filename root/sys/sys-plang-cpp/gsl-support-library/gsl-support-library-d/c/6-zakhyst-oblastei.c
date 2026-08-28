#include <stdio.h>
#include <stdlib.h>

/* Традиційне C-очищення ресурсів через мітки goto */
int process_file_c(const char* filename) {
    FILE* f = fopen(filename, "rb");
    if (!f) return -1;

    void* buffer = malloc(1024);
    if (!buffer) {
        fclose(f);
        return -2;
    }

    /* Якщо тут виникне помилка, потрібно не забути всі free та fclose */
    if (fread(buffer, 1, 1024, f) != 1024) {
        free(buffer);
        fclose(f);
        return -3;
    }

    free(buffer);
    fclose(f);
    return 0;
}

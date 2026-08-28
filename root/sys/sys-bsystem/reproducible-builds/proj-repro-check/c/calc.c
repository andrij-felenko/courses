/* calc.c */
#include "calc.h"
#include <stdio.h>

int calculate_checksum(const char *data, int length) {
    int sum = 0;
    for (int i = 0; i < length; ++i) {
        sum = (sum * 31) + (unsigned char)data[i];
    }
    return sum;
}

void print_build_banner(void) {
    /* Пастка 1: використання часу компіляції */
    printf("Calc Engine Build Date: %s %s\n", __DATE__, __TIME__);
    /* Пастка 2: використання абсолютного шляху до файлу */
    printf("Compiled from source: %s\n", __FILE__);
}

/* main.c */
#include "calc.h"
#include <stdio.h>

int main(void) {
    print_build_banner();
    const char msg[] = "Reproducible Builds Test";
    int res = calculate_checksum(msg, sizeof(msg) - 1);
    printf("Checksum result: 0x%08X\n", res);
    return 0;
}

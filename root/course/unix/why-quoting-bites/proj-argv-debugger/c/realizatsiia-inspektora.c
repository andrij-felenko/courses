#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* Вивід байтового дампа рядка у шістнадцятковому та текстовому вигляді */
static void dump_hex_string(const char *str, size_t len) {
    printf("    [hex] ");
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)str[i];
        printf("%02x ", c);
    }
    printf("\n    [asc] ");
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)str[i];
        if (isprint(c)) {
            printf(" %c ", c);
        } else if (c == '\n') {
            printf("\\n ");
        } else if (c == '\t') {
            printf("\\t ");
        } else if (c == ' ') {
            printf("·  ");
        } else {
            printf("?? ");
        }
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    printf("==================== ARGV DUMP ====================\n");
    printf("Кількість аргументів (argc): %d\n", argc);
    printf("---------------------------------------------------\n");

    for (int i = 0; i < argc; i++) {
        size_t len = strlen(argv[i]);
        printf("argv[%2d] (довжина: %3zu б) : \"%s\"\n", i, len, argv[i]);
        dump_hex_string(argv[i], len);
    }

    printf("===================================================\n");
    return 0;
}

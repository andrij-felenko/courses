/* read_nul_stream.c — Безпечне читання NUL-розділеного потоку через getdelim().
 * Збірка: cc -std=c99 -Wall -Wextra -O2 read_nul_stream.c -o read_nul_stream
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char *entry = NULL;
    size_t cap = 0;
    ssize_t len;
    size_t count = 0;

    /* Читання потоку stdin з роздільником NUL (байт 0x00) */
    while ((len = getdelim(&entry, &cap, '\0', stdin)) != -1) {
        count++;
        printf("[%zu] Запис (%zd байтів): %s\n", count, len, entry);
    }

    free(entry);
    return 0;
}

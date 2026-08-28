/* probe.c — що система обіцяє і що вміє насправді */
#define _POSIX_C_SOURCE 202405L   /* просимо контракт редакції 2024 року */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    char *path = strdup("/tmp/log");        /* strdup — POSIX, не ISO C */
    printf("редакція системи: %ld\n", sysconf(_SC_VERSION));
    printf("потоки:           %ld\n", sysconf(_SC_THREADS));
    printf("таймери:          %ld\n", sysconf(_SC_TIMERS));
    printf("межа дескрипторів:%ld\n", sysconf(_SC_OPEN_MAX));
    free(path);
    return 0;
}

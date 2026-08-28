#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void audit_environment(void) {
    const char *path = getenv("PATH");
    const char *home = getenv("HOME");
    const char *user = getenv("USER");

    printf("[ENV AUDIT]\n");
    printf("  PATH: %s\n", path ? path : "(NOT SET - CRITICAL)");
    printf("  HOME: %s\n", home ? home : "(NOT SET - FALLBACK TO /)");
    printf("  USER: %s\n", user ? user : "(NOT SET)");

    if (!home) {
        /* Безпечний фолбек: не падати на розіменуванні NULL */
        setenv("HOME", "/tmp", 1);
    }
}

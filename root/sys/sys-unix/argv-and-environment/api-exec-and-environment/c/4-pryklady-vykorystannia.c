/* Приклад на мові C: Ізольований запуск процесу з перевіркою помилок execve */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/auxv.h>

void print_system_auxv(void) {
    unsigned long page_size = getauxval(AT_PAGESZ);
    unsigned long entry_addr = getauxval(AT_ENTRY);
    unsigned long is_secure = getauxval(AT_SECURE);
    const char *platform = (const char *)getauxval(AT_PLATFORM);

    printf("=== System Auxiliary Vector Info ===\n");
    printf("Page Size   : %lu bytes\n", page_size);
    printf("Entry Point : 0x%lx\n", entry_addr);
    printf("Secure Mode : %lu\n", is_secure);
    printf("Platform    : %s\n\n", platform ? platform : "unknown");
}

int main(void) {
    print_system_auxv();

    /* Формування чітко контрольованого середовища */
    char *custom_env[] = {
        "PATH=/usr/bin:/bin",
        "LANG=C.UTF-8",
        "SECURE_TOKEN=xyz12345",
        NULL
    };

    /* Аргументи запуску команди /usr/bin/env */
    char *custom_argv[] = {
        "env",
        NULL
    };

    printf("Launching /usr/bin/env with controlled environment...\n");
    fflush(stdout);

    execve("/usr/bin/env", custom_argv, custom_env);

    /* Код після execve виконується ТІЛЬКИ в разі помилки */
    int err = errno;
    fprintf(stderr, "Failed to execute execve: %s (errno: %d)\n", strerror(err), err);

    if (err == ENOENT) {
        fprintf(stderr, "Error: Binary /usr/bin/env not found.\n");
    } else if (err == E2BIG) {
        fprintf(stderr, "Error: Environment or argument list too large.\n");
    }

    return EXIT_FAILURE;
}

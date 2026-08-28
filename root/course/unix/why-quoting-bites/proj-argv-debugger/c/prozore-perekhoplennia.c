#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <unistd.h>
#include <string.h>

typedef int (*real_execve_t)(const char *filename, char *const argv[], char *const envp[]);

/* Перехоплення системного виклику execve у просторі користувача */
int execve(const char *filename, char *const argv[], char *const envp[]) {
    real_execve_t original_execve = (real_execve_t)dlsym(RTLD_NEXT, "execve");
    if (!original_execve) {
        fprintf(stderr, "[libargv_trace] dlsym помилка: %s\n", dlerror());
        _exit(1);
    }

    fprintf(stderr, "\n[EXECVE INTERCEPT] Запуск програми: %s\n", filename);
    if (argv) {
        int i = 0;
        while (argv[i] != NULL) {
            fprintf(stderr, "  -> argv[%2d] = \"%s\" (байтів: %zu)\n", i, argv[i], strlen(argv[i]));
            i++;
        }
    }
    fprintf(stderr, "[EXECVE INTERCEPT] ----------------------------------------\n\n");

    return original_execve(filename, argv, envp);
}

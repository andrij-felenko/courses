#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/stat.h>

void perform_full_system_audit(void) {
    printf("=== ДІАГНОСТИКА СЕРЕДОВИЩА ПРОЦЕСУ ===\n");

    /* 1. Перевірка TTY */
    int tty_in = isatty(fileno(stdin));
    int tty_out = isatty(fileno(stdout));
    printf("[TTY] stdin: %s, stdout: %s\n",
           tty_in ? "TTY (interactive)" : "PIPE/SOCKET (service)",
           tty_out ? "TTY (_IOLBF)" : "PIPE/SOCKET (_IOFBF)");

    /* 2. Перевірка CWD */
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd))) {
        printf("[CWD] Поточний каталог: %s\n", cwd);
        if (cwd[0] == '/' && cwd[1] == '\0') {
            printf("  [УВАГА] Процес запущено в корені /! Відносні шляхи будуть хибними.\n");
        }
    }

    /* 3. Перевірка критичних змінних */
    printf("[ENV] PATH: %s\n", getenv("PATH") ? getenv("PATH") : "(NULL)");
    printf("[ENV] HOME: %s\n", getenv("HOME") ? getenv("HOME") : "(NULL)");

    /* 4. Ліміти дескрипторів */
    struct rlimit rl;
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0) {
        printf("[LIMITS] NOFILE soft: %lu, hard: %lu\n",
               (unsigned long)rl.rlim_cur, (unsigned long)rl.rlim_max);
    }

    /* 5. Тестовий запис у /tmp */
    FILE *tmp_test = fopen("/tmp/.audit_service_probe", "w");
    if (tmp_test) {
        printf("[FS] Запис у /tmp: УСПІХ\n");
        fclose(tmp_test);
        unlink("/tmp/.audit_service_probe");
    } else {
        perror("[FS] Помилка запису у /tmp");
    }
    printf("=========================================\n");
}

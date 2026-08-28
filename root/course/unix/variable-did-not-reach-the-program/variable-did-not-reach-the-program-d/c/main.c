#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    /* Встановлюємо локальну змінну процесу */
    if (setenv("SERVICE_PORT", "9090", 1) != 0) {
        perror("setenv");
        return EXIT_FAILURE;
    }

    /* Формуємо явний білий список envp для дочірнього процесу */
    char *child_env[] = {
        "PATH=/usr/bin:/bin",
        "SERVICE_PORT=9090",
        "DATABASE_URL=postgres://db.internal:5432/app",
        NULL /* Обов'язковий завершальний нульовий покажчик */
    };

    char *child_argv[] = { "printenv", NULL };

    pid_t pid = fork();
    if (pid == 0) {
        /* Дочірній процес: виконуємо execve з власним масивом envp */
        execve("/usr/bin/printenv", child_argv, child_env);
        perror("execve");
        _exit(127);
    }

    waitpid(pid, NULL, 0);
    return EXIT_SUCCESS;
}

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/wait.h>
#include <sys/types.h>

#define PROC_BUF_SIZE 4096

/* Функція інспекції середовища процесу через /proc/[pid]/environ */
static void inspect_process_environ(pid_t target_pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/environ", target_pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[Помилка] Не вдалося відкрити %s: %s\n", path, strerror(errno));
        return;
    }

    printf("\n=== Зліпок /proc/%d/environ (роздільник null-byte) ===\n", target_pid);

    char buffer[PROC_BUF_SIZE];
    ssize_t bytes_read;
    size_t var_count = 0;

    while ((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        ssize_t start = 0;
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buffer[i] == '\0') {
                if (i > start) {
                    var_count++;
                    printf("  [%02zu] %.*s\n", var_count, (int)(i - start), &buffer[start]);
                }
                start = i + 1;
            }
        }
    }

    if (bytes_read < 0) {
        fprintf(stderr, "[Помилка] Помилка читання з %s: %s\n", path, strerror(errno));
    }

    close(fd);
    printf("=== Усього виявлено змінних у пам'яті: %zu ===\n\n", var_count);
}

/* Безпечний запуск процесу з кастомним масивом envp */
int main(void) {
    printf("[Лаунчер C] Підготовка ізольованого середовища для дочірнього процесу...\n");

    /* Формуємо явний білий список змінних */
    char *custom_env[] = {
        "PATH=/usr/bin:/bin",
        "APP_ENV=production",
        "DATABASE_URL=postgres://app_user:s3cr3t@127.0.0.1:5432/production_db",
        "LOG_LEVEL=info",
        "CUSTOM_INJECTED_VAR=success_reach",
        NULL
    };

    /* Аргументи для запуску sleep, щоб встигнути оглянути /proc */
    char *child_argv[] = {
        "sleep",
        "1",
        NULL
    };

    pid_t pid = fork();
    if (pid < 0) {
        perror("[Помилка] fork");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: виконуємо execve з власним масивом envp */
        execve("/bin/sleep", child_argv, custom_env);

        /* Якщо execve повернув керування — сталася помилка */
        perror("[Помилка дочірнього процесу] execve");
        _exit(127);
    }

    /* Батьківський процес: інспектуємо пам'ять дитини через /proc */
    usleep(50000); /* Коротка пауза, щоб дитина встигла виконати execve */
    inspect_process_environ(pid);

    int status;
    if (waitpid(pid, &status, 0) < 0) {
        perror("[Помилка] waitpid");
        return EXIT_FAILURE;
    }

    if (WIFEXITED(status)) {
        printf("[Лаунчер C] Дочірній процес %d завершився з кодом %d.\n", pid, WEXITSTATUS(status));
    }

    return EXIT_SUCCESS;
}

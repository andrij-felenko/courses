#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/types.h>

/* Структура для опису однієї команди конвеєра */
typedef struct {
    char *const *argv;
} pipeline_stage;

/* Запуск конвеєра з n команд: stage[0] | stage[1] | ... | stage[n-1] */
int run_pipeline(const pipeline_stage *stages, size_t n) {
    if (n == 0) return 0;
    if (n == 1) {
        pid_t pid = fork();
        if (pid == 0) {
            execvp(stages[0].argv[0], stages[0].argv);
            perror("execvp");
            _exit(127);
        }
        int status;
        waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    /* Для n команд потрібно (n - 1) каналів */
    int pipes[n - 1][2];
    for (size_t i = 0; i < n - 1; i++) {
        /* Встановлюємо O_CLOEXEC, щоб дескриптори не витікали при execvp */
        if (pipe2(pipes[i], O_CLOEXEC) < 0) {
            perror("pipe2");
            return -1;
        }
    }

    pid_t pids[n];

    for (size_t i = 0; i < n; i++) {
        pids[i] = fork();
        if (pids[i] < 0) {
            perror("fork");
            return -1;
        }

        if (pids[i] == 0) {
            /* Дочірній процес: налаштовуємо вхідний дескриптор */
            if (i > 0) {
                /* Читаємо з попереднього каналу */
                if (dup2(pipes[i - 1][0], STDIN_FILENO) < 0) {
                    perror("dup2 stdin");
                    _exit(1);
                }
            }

            /* Налаштовуємо вихідний дескриптор */
            if (i < n - 1) {
                /* Пишемо в наступний канал */
                if (dup2(pipes[i][1], STDOUT_FILENO) < 0) {
                    perror("dup2 stdout");
                    _exit(1);
                }
            }

            /* Закриваємо всі успадковані дескриптори каналів у дочірньому процесі */
            for (size_t j = 0; j < n - 1; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            /* Заміщуємо образ процесу цільовою програмою */
            execvp(stages[i].argv[0], stages[i].argv);
            perror("execvp");
            _exit(127);
        }
    }

    /* Батьківський процес: ЗАКРИВАЄМО ВСІ КІНЦІ КАНАЛІВ! */
    for (size_t i = 0; i < n - 1; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    /* Очікуємо завершення всіх дочірніх процесів */
    int last_status = 0;
    for (size_t i = 0; i < n; i++) {
        int status;
        waitpid(pids[i], &status, 0);
        if (i == n - 1 && WIFEXITED(status)) {
            last_status = WEXITSTATUS(status);
        }
    }

    return last_status;
}

int main(void) {
    /* Приклад конвеєра: cat /etc/passwd | grep -v nobody | cut -d: -f1 */
    char *cmd0[] = {"cat", "/etc/passwd", NULL};
    char *cmd1[] = {"grep", "-v", "nobody", NULL};
    char *cmd2[] = {"cut", "-d:", "-f1", NULL};

    pipeline_stage stages[] = {
        {cmd0},
        {cmd1},
        {cmd2}
    };

    return run_pipeline(stages, 3);
}

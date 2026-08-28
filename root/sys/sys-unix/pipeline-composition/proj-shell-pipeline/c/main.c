#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <string.h>
#include <fcntl.h>

// Структура опису окремої команди у конвеєрі
typedef struct {
    char **argv; // Масив аргументів (закінчується NULL)
} command_t;

int execute_pipeline(command_t *cmds, size_t num_cmds) {
    if (num_cmds == 0) return 0;

    // Створюємо масив каналів (num_cmds - 1 каналів)
    int (*pipes)[2] = NULL;
    if (num_cmds > 1) {
        pipes = malloc(sizeof(int[2]) * (num_cmds - 1));
        if (!pipes) {
            perror("malloc failed");
            return -1;
        }

        for (size_t i = 0; i < num_cmds - 1; ++i) {
            if (pipe2(pipes[i], O_CLOEXEC) == -1) {
                perror("pipe2 failed");
                free(pipes);
                return -1;
            }
        }
    }

    pid_t *pids = malloc(sizeof(pid_t) * num_cmds);
    if (!pids) {
        perror("malloc pids failed");
        if (pipes) free(pipes);
        return -1;
    }

    for (size_t i = 0; i < num_cmds; ++i) {
        pids[i] = fork();
        if (pids[i] == -1) {
            perror("fork failed");
            break;
        }

        if (pids[i] == 0) {
            // --- ДОЧІРНІЙ ПРОЦЕС i ---

            // 1. Вхідний потік (stdin)
            if (i > 0) {
                if (dup2(pipes[i - 1][0], STDIN_FILENO) == -1) {
                    perror("dup2 stdin failed");
                    exit(EXIT_FAILURE);
                }
            }

            // 2. Вихідний потік (stdout)
            if (i < num_cmds - 1) {
                if (dup2(pipes[i][1], STDOUT_FILENO) == -1) {
                    perror("dup2 stdout failed");
                    exit(EXIT_FAILURE);
                }
            }

            // 3. Закриваємо УСІ канали у дочірньому процесі
            if (pipes) {
                for (size_t j = 0; j < num_cmds - 1; ++j) {
                    close(pipes[j][0]);
                    close(pipes[j][1]);
                }
            }

            // 4. Виконуємо команду
            execvp(cmds[i].argv[0], cmds[i].argv);
            perror("execvp failed");
            exit(EXIT_FAILURE);
        }
    }

    // --- БАТЬКІВСЬКИЙ ПРОЦЕС ---
    // Закриваємо всі кінці каналів у батька!
    if (pipes) {
        for (size_t j = 0; j < num_cmds - 1; ++j) {
            close(pipes[j][0]);
            close(pipes[j][1]);
        }
        free(pipes);
    }

    // Чекаємо завершення усіх створених дочірніх процесів
    int last_status = 0;
    for (size_t i = 0; i < num_cmds; ++i) {
        if (pids[i] > 0) {
            int status = 0;
            waitpid(pids[i], &status, 0);
            if (i == num_cmds - 1) {
                last_status = status;
            }
        }
    }

    free(pids);
    return WIFEXITED(last_status) ? WEXITSTATUS(last_status) : -1;
}

int main(void) {
    // Еквівалент командного рядка: ls -l | grep txt | wc -l
    char *cmd1[] = {"ls", "-l", NULL};
    char *cmd2[] = {"grep", "txt", NULL};
    char *cmd3[] = {"wc", "-l", NULL};

    command_t pipeline[] = {
        {.argv = cmd1},
        {.argv = cmd2},
        {.argv = cmd3}
    };

    printf("Executing pipeline: ls -l | grep txt | wc -l\n");
    int exit_code = execute_pipeline(pipeline, 3);
    printf("Pipeline finished with exit code: %d\n", exit_code);

    return 0;
}

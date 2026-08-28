/* mini_shell.c — POSIX C реалізація ядра оркестрації процесів */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LINE 1024
#define MAX_ARGS 64

/* Розбиття рядка на аргументи за пробілами */
static int tokenize(char *line, char **args) {
    int count = 0;
    char *token = strtok(line, " \t\n\r");
    while (token != NULL && count < MAX_ARGS - 1) {
        args[count++] = token;
        token = strtok(NULL, " \t\n\r");
    }
    args[count] = NULL;
    return count;
}

/* Обробка вбудованих команд у батьківському процесі */
static int handle_builtin(char **args) {
    if (args[0] == NULL) return 1;
    
    if (strcmp(args[0], "exit") == 0) {
        exit(0);
    }
    if (strcmp(args[0], "cd") == 0) {
        const char *dir = args[1] ? args[1] : getenv("HOME");
        if (!dir) dir = "/";
        if (chdir(dir) != 0) {
            perror("mini-shell: cd");
        }
        return 1; /* Оброблено як builtin */
    }
    return 0; /* Зовнішня команда */
}

/* Виконання одиничної зовнішньої команди */
static void execute_simple_command(char **args) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("mini-shell: fork failed");
        return;
    }
    if (pid == 0) {
        /* Дочірній процес */
        execvp(args[0], args);
        perror("mini-shell: execvp failed");
        exit(127);
    } else {
        /* Батьківський процес чекає завершення */
        int status;
        waitpid(pid, &status, 0);
    }
}

/* Виконання конвеєра з двох команд: cmd1 | cmd2 */
static void execute_pipeline(char **cmd1_args, char **cmd2_args) {
    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("mini-shell: pipe failed");
        return;
    }

    /* Створення першого дочірнього процесу (cmd1) */
    pid_t pid1 = fork();
    if (pid1 == 0) {
        /* Перенаправляємо stdout у pipe write end */
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd1_args[0], cmd1_args);
        perror("mini-shell: execvp cmd1 failed");
        exit(127);
    }

    /* Створення другого дочірнього процесу (cmd2) */
    pid_t pid2 = fork();
    if (pid2 == 0) {
        /* Перенаправляємо stdin з pipe read end */
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd2_args[0], cmd2_args);
        perror("mini-shell: execvp cmd2 failed");
        exit(127);
    }

    /* Батьківський процес обов'язково закриває свої копії дескрипторів каналу */
    close(pipefd[0]);
    close(pipefd[1]);

    /* Очікування завершення обох дочірніх процесів */
    int status;
    waitpid(pid1, &status, 0);
    waitpid(pid2, &status, 0);
}

int main(void) {
    char line[MAX_LINE];

    while (1) {
        printf("mini-shell> ");
        fflush(stdout);

        if (!fgets(line, sizeof(line), stdin)) {
            break; /* EOF (Ctrl+D) */
        }

        /* Пошук символу конвеєра '|' */
        char *pipe_pos = strchr(line, '|');
        if (pipe_pos != NULL) {
            *pipe_pos = '\0';
            char *left_part = line;
            char *right_part = pipe_pos + 1;

            char *cmd1_args[MAX_ARGS];
            char *cmd2_args[MAX_ARGS];

            if (tokenize(left_part, cmd1_args) > 0 && tokenize(right_part, cmd2_args) > 0) {
                execute_pipeline(cmd1_args, cmd2_args);
            }
        } else {
            char *args[MAX_ARGS];
            if (tokenize(line, args) > 0) {
                if (!handle_builtin(args)) {
                    execute_simple_command(args);
                }
            }
        }
    }

    printf("\nGoodbye!\n");
    return 0;
}

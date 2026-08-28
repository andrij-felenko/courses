#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>

#define MAX_ARGS 64

struct RedirectionConfig {
    char *infile;
    char *outfile;
    int append_mode;
    int merge_stderr;
};

static void execute_command(char **argv, struct RedirectionConfig *cfg) {
    if (cfg->infile) {
        int fd_in = open(cfg->infile, O_RDONLY);
        if (fd_in < 0) {
            perror("open infile failed");
            exit(EXIT_FAILURE);
        }
        if (dup2(fd_in, STDIN_FILENO) < 0) {
            perror("dup2 stdin failed");
            close(fd_in);
            exit(EXIT_FAILURE);
        }
        close(fd_in);
    }

    if (cfg->outfile) {
        int flags = O_WRONLY | O_CREAT | (cfg->append_mode ? O_APPEND : O_TRUNC);
        int fd_out = open(cfg->outfile, flags, 0644);
        if (fd_out < 0) {
            perror("open outfile failed");
            exit(EXIT_FAILURE);
        }
        if (dup2(fd_out, STDOUT_FILENO) < 0) {
            perror("dup2 stdout failed");
            close(fd_out);
            exit(EXIT_FAILURE);
        }
        close(fd_out);
    }

    if (cfg->merge_stderr) {
        if (dup2(STDOUT_FILENO, STDERR_FILENO) < 0) {
            perror("dup2 merge stderr failed");
            exit(EXIT_FAILURE);
        }
    }

    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи] [перенаправлення...]\n", argv[0]);
        fprintf(stderr, "Приклад: %s ls -la > out.txt 2>&1\n", argv[0]);
        return EXIT_FAILURE;
    }

    char *cmd_args[MAX_ARGS];
    int arg_idx = 0;
    struct RedirectionConfig cfg = {NULL, NULL, 0, 0};

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "<") == 0 && i + 1 < argc) {
            cfg.infile = argv[++i];
        } else if (strcmp(argv[i], ">") == 0 && i + 1 < argc) {
            cfg.outfile = argv[++i];
            cfg.append_mode = 0;
        } else if (strcmp(argv[i], ">>") == 0 && i + 1 < argc) {
            cfg.outfile = argv[++i];
            cfg.append_mode = 1;
        } else if (strcmp(argv[i], "2>&1") == 0) {
            cfg.merge_stderr = 1;
        } else {
            if (arg_idx < MAX_ARGS - 1) {
                cmd_args[arg_idx++] = argv[i];
            }
        }
    }
    cmd_args[arg_idx] = NULL;

    if (arg_idx == 0) {
        fprintf(stderr, "Помилка: не вказано команду для виконання\n");
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес */
        execute_command(cmd_args, &cfg);
    } else {
        /* Батьківський процес */
        int status;
        if (waitpid(pid, &status, 0) < 0) {
            perror("waitpid failed");
            return EXIT_FAILURE;
        }
        if (WIFEXITED(status)) {
            printf("[Процес завершено з кодом: %d]\n", WEXITSTATUS(status));
        }
    }

    return EXIT_SUCCESS;
}

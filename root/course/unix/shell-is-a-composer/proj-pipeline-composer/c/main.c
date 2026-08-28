#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <termios.h>
#include <errno.h>

typedef struct {
    char *const *argv;
} Command;

typedef struct {
    int last_status;
    int pipefail_status;
    int *all_statuses;
    size_t count;
} PipelineResult;

PipelineResult run_pipeline(const Command *cmds, size_t num_cmds) {
    PipelineResult res = { .last_status = -1, .pipefail_status = 0, .all_statuses = NULL, .count = num_cmds };
    if (num_cmds == 0) return res;

    res.all_statuses = malloc(sizeof(int) * num_cmds);
    if (!res.all_statuses) {
        perror("malloc");
        return res;
    }

    int (*pipes)[2] = NULL;
    if (num_cmds > 1) {
        pipes = malloc(sizeof(int[2]) * (num_cmds - 1));
        if (!pipes) {
            perror("malloc pipes");
            free(res.all_statuses);
            res.all_statuses = NULL;
            return res;
        }
        for (size_t i = 0; i < num_cmds - 1; ++i) {
            if (pipe2(pipes[i], O_CLOEXEC) == -1) {
                perror("pipe2");
                for (size_t j = 0; j < i; ++j) {
                    close(pipes[j][0]);
                    close(pipes[j][1]);
                }
                free(pipes);
                free(res.all_statuses);
                res.all_statuses = NULL;
                return res;
            }
        }
    }

    pid_t *pids = malloc(sizeof(pid_t) * num_cmds);
    pid_t pgid = 0;
    int is_interactive = isatty(STDIN_FILENO);
    pid_t shell_pgid = getpgrp();

    for (size_t i = 0; i < num_cmds; ++i) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            break;
        }

        if (pid == 0) {
            // === ТІЛО ДОЧІРНЬОГО ПРОЦЕСУ ===
            pid_t cur_pid = getpid();
            pid_t target_pgid = (i == 0) ? cur_pid : pgid;
            setpgid(0, target_pgid);

            if (i > 0) {
                if (dup2(pipes[i - 1][0], STDIN_FILENO) == -1) {
                    perror("dup2 stdin");
                    _exit(127);
                }
            }

            if (i < num_cmds - 1) {
                if (dup2(pipes[i][1], STDOUT_FILENO) == -1) {
                    perror("dup2 stdout");
                    _exit(127);
                }
            }

            if (num_cmds > 1) {
                for (size_t j = 0; j < num_cmds - 1; ++j) {
                    close(pipes[j][0]);
                    close(pipes[j][1]);
                }
            }

            execvp(cmds[i].argv[0], cmds[i].argv);
            perror("execvp");
            _exit(127);
        }

        // === ТІЛО БАТЬКІВСЬКОГО ПРОЦЕСУ ===
        pids[i] = pid;
        if (i == 0) {
            pgid = pid;
        }
        setpgid(pid, pgid);
    }

    if (num_cmds > 1) {
        for (size_t i = 0; i < num_cmds - 1; ++i) {
            close(pipes[i][0]);
            close(pipes[i][1]);
        }
        free(pipes);
    }

    if (is_interactive && pgid > 0) {
        tcsetpgrp(STDIN_FILENO, pgid);
    }

    int pipefail_code = 0;
    for (size_t i = 0; i < num_cmds; ++i) {
        int wstatus = 0;
        while (waitpid(pids[i], &wstatus, 0) == -1) {
            if (errno == EINTR) continue;
            perror("waitpid");
            break;
        }

        int exit_code = 0;
        if (WIFEXITED(wstatus)) {
            exit_code = WEXITSTATUS(wstatus);
        } else if (WIFSIGNALED(wstatus)) {
            exit_code = 128 + WTERMSIG(wstatus);
        }

        res.all_statuses[i] = exit_code;
        if (exit_code != 0) {
            pipefail_code = exit_code;
        }
    }

    if (is_interactive) {
        tcsetpgrp(STDIN_FILENO, shell_pgid);
    }

    res.last_status = res.all_statuses[num_cmds - 1];
    res.pipefail_status = pipefail_code;

    free(pids);
    return res;
}

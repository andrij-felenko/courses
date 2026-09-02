#define _GNU_SOURCE
#include "launch.h"
#include "jobs.h"

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

pid_t launch_stage(const struct launch_ctx *ctx)
{
    const pid_t child = fork();

    if (child < 0) {
        perror("fork");
        return -1;
    }

    if (child == 0) {
        /* --- нащадок --- */
        const pid_t pgid = (ctx->pgid == 0) ? getpid() : ctx->pgid;

        /* Ту саму дію робить і батько: хто перший встиг, той і створив групу.
         * Саме це знімає гонку між setpgid() у батька та execve() в нащадка. */
        if (setpgid(0, pgid) < 0 && errno != EACCES) {
            _exit(126);
        }
        if (ctx->foreground && ctx->tty_fd >= 0) {
            tcsetpgrp(ctx->tty_fd, pgid);
        }

        /* Оболонка ігнорувала термінальні сигнали — програмі потрібна типова дія. */
        signal(SIGINT,  SIG_DFL);
        signal(SIGQUIT, SIG_DFL);
        signal(SIGTSTP, SIG_DFL);
        signal(SIGTTIN, SIG_DFL);
        signal(SIGTTOU, SIG_DFL);
        signal(SIGCHLD, SIG_DFL);

        if (ctx->in_fd != STDIN_FILENO && dup2(ctx->in_fd, STDIN_FILENO) < 0) {
            perror("dup2(stdin)");
            _exit(126);
        }
        if (ctx->out_fd != STDOUT_FILENO && dup2(ctx->out_fd, STDOUT_FILENO) < 0) {
            perror("dup2(stdout)");
            _exit(126);
        }
        /* Копії дескрипторів каналу після dup2 більше не потрібні:
         * зайвий відкритий кінець запису означав би, що читач не побачить EOF. */
        for (int i = 0; i < ctx->nclose; i++) {
            if (ctx->close_fds[i] > STDERR_FILENO) {
                close(ctx->close_fds[i]);
            }
        }

        execvp(ctx->argv[0], ctx->argv);
        fprintf(stderr, "%s: %s\n", ctx->argv[0], strerror(errno));
        _exit(errno == ENOENT ? 127 : 126);
    }

    /* --- батько --- */
    {
        const pid_t pgid = (ctx->pgid == 0) ? child : ctx->pgid;

        if (setpgid(child, pgid) < 0 && errno != EACCES && errno != ESRCH) {
            perror("setpgid(батько)");
        }
        if (ctx->foreground) {
            give_terminal_to(pgid);
        }
    }
    return child;
}

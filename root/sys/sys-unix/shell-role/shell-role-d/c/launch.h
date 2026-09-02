/* Запуск однієї ланки конвеєра через fork() + execvp(). */
#ifndef LAUNCH_H
#define LAUNCH_H

#include <stdbool.h>
#include <sys/types.h>

struct launch_ctx {
    char *const *argv;      /* NULL-термінований вектор аргументів */
    int in_fd;              /* що стане stdin нащадка */
    int out_fd;             /* що стане stdout нащадка */
    const int *close_fds;   /* дескриптори оболонки, зайві для нащадка */
    int nclose;
    pid_t pgid;             /* 0 — нащадок стає лідером власної групи */
    bool foreground;
    int tty_fd;             /* -1, якщо керування завданнями вимкнене */
};

pid_t launch_stage(const struct launch_ctx *ctx);

#endif /* LAUNCH_H */

#include "spawn_stage.h"

#include <errno.h>
#include <signal.h>
#include <spawn.h>
#include <unistd.h>

extern char **environ;

pid_t spawn_pipeline_stage(const char *path, char *const argv[],
                           const struct spawn_io *io)
{
    posix_spawn_file_actions_t actions;
    posix_spawnattr_t attr;
    sigset_t to_default, empty;
    pid_t pid = -1;
    int rc;

    rc = posix_spawn_file_actions_init(&actions);
    if (rc != 0) {
        errno = rc;
        return -1;
    }
    rc = posix_spawnattr_init(&attr);
    if (rc != 0) {
        posix_spawn_file_actions_destroy(&actions);
        errno = rc;
        return -1;
    }

    /* Дії над дескрипторами виконує сама бібліотека вже в новому процесі,
     * тож стек батька, який vfork-подібний clone() ділить із нащадком,
     * не чіпається взагалі. */
    if (io->in_fd != STDIN_FILENO) {
        rc = posix_spawn_file_actions_adddup2(&actions, io->in_fd, STDIN_FILENO);
    }
    if (rc == 0 && io->out_fd != STDOUT_FILENO) {
        rc = posix_spawn_file_actions_adddup2(&actions, io->out_fd, STDOUT_FILENO);
    }
    for (int i = 0; rc == 0 && i < io->nclose; i++) {
        if (io->close_fds[i] > STDERR_FILENO) {
            rc = posix_spawn_file_actions_addclose(&actions, io->close_fds[i]);
        }
    }

    /* Групу процесів виставляє ядро між clone() та execve():
     * вікна гонки, як із ручним setpgid(), тут просто немає. */
    sigemptyset(&empty);
    sigemptyset(&to_default);
    sigaddset(&to_default, SIGINT);
    sigaddset(&to_default, SIGQUIT);
    sigaddset(&to_default, SIGTSTP);
    sigaddset(&to_default, SIGTTIN);
    sigaddset(&to_default, SIGTTOU);
    sigaddset(&to_default, SIGCHLD);

    if (rc == 0) {
        rc = posix_spawnattr_setpgroup(&attr, io->pgid);
    }
    if (rc == 0) {
        rc = posix_spawnattr_setsigdefault(&attr, &to_default);
    }
    if (rc == 0) {
        rc = posix_spawnattr_setsigmask(&attr, &empty);
    }
    if (rc == 0) {
        rc = posix_spawnattr_setflags(&attr, POSIX_SPAWN_SETPGROUP
                                             | POSIX_SPAWN_SETSIGDEF
                                             | POSIX_SPAWN_SETSIGMASK);
    }
    if (rc == 0) {
        /* posix_spawnp повертає код помилки значенням, а не через errno. */
        rc = posix_spawnp(&pid, path, &actions, &attr, argv, environ);
    }

    posix_spawn_file_actions_destroy(&actions);
    posix_spawnattr_destroy(&attr);

    if (rc != 0) {
        errno = rc;
        return -1;
    }
    return pid;
}

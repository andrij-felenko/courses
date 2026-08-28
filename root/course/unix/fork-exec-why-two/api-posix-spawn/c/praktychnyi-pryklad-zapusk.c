#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <spawn.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

int spawn_grep_process(int input_pipe_fd, const char *search_pattern, pid_t *child_pid) {
    posix_spawn_file_actions_t file_actions;
    posix_spawnattr_t attributes;
    int err;

    /* 1. Ініціалізація структур налаштувань */
    if ((err = posix_spawn_file_actions_init(&file_actions)) != 0) {
        return err;
    }
    if ((err = posix_spawnattr_init(&attributes)) != 0) {
        posix_spawn_file_actions_destroy(&file_actions);
        return err;
    }

    /* 2. Налаштування дескрипторів: прив'язка каналу до STDIN */
    if ((err = posix_spawn_file_actions_adddup2(&file_actions, input_pipe_fd, STDIN_FILENO)) != 0) {
        goto cleanup;
    }
    /* Якщо канал не був дескриптором 0, закриваємо дублікат */
    if (input_pipe_fd != STDIN_FILENO) {
        if ((err = posix_spawn_file_actions_addclose(&file_actions, input_pipe_fd)) != 0) {
            goto cleanup;
        }
    }

    /* 3. Налаштування сигналів та групи процесів */
    sigset_t default_signals;
    sigemptyset(&default_signals);
    sigaddset(&default_signals, SIGPIPE);
    if ((err = posix_spawnattr_setsigdefault(&attributes, &default_signals)) != 0) {
        goto cleanup;
    }

    /* Встановлюємо прапорці: нова група процесів і відновлення SIGPIPE */
    short flags = POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETPGROUP;
    if ((err = posix_spawnattr_setflags(&attributes, flags)) != 0) {
        goto cleanup;
    }
    if ((err = posix_spawnattr_setpggroup(&attributes, 0)) != 0) {
        goto cleanup;
    }

    /* 4. Підготовка аргументів та середовища */
    char *const argv[] = {
        (char *)"grep",
        (char *)search_pattern,
        NULL
    };
    extern char **environ;

    /* 5. Запуск нової програми з пошуком у PATH */
    err = posix_spawnp(child_pid, "grep", &file_actions, &attributes, argv, environ);

cleanup:
    posix_spawn_file_actions_destroy(&file_actions);
    posix_spawnattr_destroy(&attributes);
    return err;
}

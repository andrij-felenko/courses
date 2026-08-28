#include <spawn.h>
#include <unistd.h>

int spawn_clean_process(const char *path, char *const argv[], char *const envp[]) {
    posix_spawn_file_actions_t actions;
    posix_spawn_file_actions_init(&actions);

    /* Закриваємо конкретні дескриптори або налаштовуємо перенаправлення */
    posix_spawn_file_actions_addclose(&actions, 3);
    posix_spawn_file_actions_addclose(&actions, 4);

    pid_t pid;
    int status = posix_spawn(&pid, path, &actions, NULL, argv, envp);
    posix_spawn_file_actions_destroy(&actions);

    return status == 0 ? (int)pid : -1;
}

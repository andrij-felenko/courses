#include <spawn.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>

extern char **environ;

int main(void) {
    posix_spawn_file_actions_t acts;
    posix_spawn_file_actions_init(&acts);
    posix_spawn_file_actions_addopen(&acts, STDOUT_FILENO, "out.txt",
                                     O_WRONLY | O_CREAT | O_TRUNC, 0644);
    posix_spawn_file_actions_adddup2(&acts, STDOUT_FILENO, STDERR_FILENO);

    posix_spawnattr_t attr;
    posix_spawnattr_init(&attr);
    sigset_t none;
    sigemptyset(&none);
    posix_spawnattr_setsigmask(&attr, &none);
    posix_spawnattr_setflags(&attr, POSIX_SPAWN_SETSIGMASK);

    char *argv[] = { "ls", "-l", NULL };
    pid_t pid;
    int rc = posix_spawnp(&pid, "ls", &acts, &attr, argv, environ);

    posix_spawn_file_actions_destroy(&acts);
    posix_spawnattr_destroy(&attr);

    if (rc != 0) {
        fprintf(stderr, "запустити не вдалося: %s\n", strerror(rc));
        return 1;
    }
    int status;
    waitpid(pid, &status, 0);
    return 0;
}

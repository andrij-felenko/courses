#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* Безпечний запуск процесу без участі оболонки */
int safe_run_command(const char *file, const char *arg1, const char *arg2) {
    pid_t pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid == 0) {
        /* Дочірній процес: пряма передача масиву покажчиків */
        char *const argv[] = {(char *)file, (char *)arg1, (char *)arg2, NULL};
        execvp(file, argv);
        _exit(127);
    }

    int status = 0;
    waitpid(pid, &status, 0);
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

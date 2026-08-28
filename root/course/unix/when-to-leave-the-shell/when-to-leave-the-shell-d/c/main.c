#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

/* Безпечний запуск процесу в C без участі оболонки */
int safe_exec_c(const char *branch) {
    pid_t pid = fork();
    if (pid == 0) {
        /* Масив argv передається безпосередньо ядру: спецсимволи не інтерпретуються */
        char *const argv[] = {"git", "checkout", (char *)branch, NULL};
        execvp("git", argv);
        _exit(127);
    }
    int status;
    waitpid(pid, &status, 0);
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

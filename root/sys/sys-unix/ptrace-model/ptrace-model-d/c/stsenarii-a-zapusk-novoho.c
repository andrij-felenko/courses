#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>

void launch_target_under_trace(const char *binary_path) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        /* Дочірній процес: оголошуємо дозвіл на трасування */
        if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
            perror("ptrace(TRACEME) failed");
            exit(EXIT_FAILURE);
        }
        /* Призупиняємо виконання до того, как батько налаштує опції */
        raise(SIGSTOP);
        execl(binary_path, binary_path, NULL);
        perror("execl failed");
        exit(EXIT_FAILURE);
    } else {
        /* Батьківський процес (Tracer) */
        int status;
        waitpid(pid, &status, 0);
        if (WIFSTOPPED(status)) {
            printf("[Tracer] Tracee stopped successfully, signal: %d\n", WSTOPSIG(status));
        }
        /* Продовжуємо виконання цільової програми */
        ptrace(PTRACE_CONT, pid, NULL, NULL);
    }
}

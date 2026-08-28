#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int run_and_inspect(char *const argv[]) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }

    if (pid == 0) {
        // Дочірній процес: заміна образу програми
        execvp(argv[0], argv);
        perror("execvp");
        _exit(127); // Помилка запуску програми
    }

    // Батьківський процес: очікування завершення
    int wstatus;
    if (waitpid(pid, &wstatus, 0) < 0) {
        perror("waitpid");
        return -1;
    }

    if (WIFEXITED(wstatus)) {
        int code = WEXITSTATUS(wstatus);
        printf("[C] Процес PID %d завершився з кодом: %d\n", pid, code);
        return code;
    } else if (WIFSIGNALED(wstatus)) {
        int sig = WTERMSIG(wstatus);
        printf("[C] Процес PID %d вбито сигналом: %d\n", pid, sig);
        return 128 + sig;
    }

    return -1;
}

#include <stdio.h>
#include <sys/wait.h>

void inspect_c(int wstatus) {
    if (WIFEXITED(wstatus)) {
        int exit_code = WEXITSTATUS(wstatus);
        printf("Нормальний вихід з кодом: %d\n", exit_code);
    } else if (WIFSIGNALED(wstatus)) {
        int sig_num = WTERMSIG(wstatus);
        printf("Вбито сигналом: %d\n", sig_num);
        if (WCOREDUMP(wstatus)) {
            printf("Записано core dump.\n");
        }
    } else if (WIFSTOPPED(wstatus)) {
        printf("Зупинено сигналом: %d\n", WSTOPSIG(wstatus));
    }
}

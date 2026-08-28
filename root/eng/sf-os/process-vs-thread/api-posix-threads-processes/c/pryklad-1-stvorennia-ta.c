#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        // Код дочірнього процесу
        printf("[Дочірній процес] PID = %d, батьківський PID = %d\n",
               getpid(), getppid());
        _exit(42); // Завершення без скидання спільних буферів stdio
    }

    // Код батьківського процесу
    int wstatus = 0;
    pid_t child_pid = waitpid(pid, &wstatus, 0);

    if (child_pid > 0 && WIFEXITED(wstatus)) {
        printf("[Батьківський процес] Нащадок %d завершився з кодом %d\n",
               child_pid, WEXITSTATUS(wstatus));
    }

    return EXIT_SUCCESS;
}

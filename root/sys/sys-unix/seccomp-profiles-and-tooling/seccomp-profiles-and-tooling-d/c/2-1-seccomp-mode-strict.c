#include <stdio.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>

int main(void) {
    // Вмикаємо строгий режим Seccomp
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT) == -1) {
        perror("prctl(PR_SET_SECCOMP)");
        return 1;
    }

    // Запис у stdout дозволений (fd 1)
    write(STDOUT_FILENO, "Strict Mode активний\n", 29);

    // Спроба викликати getpid() призведе до SIGKILL від ядра
    getpid();

    return 0;
}

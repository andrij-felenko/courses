#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <string.h>
#include <errno.h>

int main(void) {
    printf("[Батько PID %d] Запуск життєвого циклу процесу...\n", getpid());

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork помилка");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Фаза 1 і 2: Дитина народилася й виконує роботу */
        printf("  [Дитина PID %d] Я народилася! Мій батько PPID = %d\n", getpid(), getppid());
        printf("  [Дитина PID %d] Працюю (стан TASK_RUNNING)...\n", getpid());
        usleep(100000); /* 100 мс активності */

        printf("  [Дитина PID %d] Засинаю в TASK_INTERRUPTIBLE на 1 секунду...\n", getpid());
        sleep(1);

        printf("  [Дитина PID %d] Завершуюся через exit(42)...\n", getpid());
        exit(42); /* Фаза 3: Перехід у do_exit() */
    }

    /* Батьківський процес */
    printf("[Батько PID %d] Дитину створено з PID %d. Чекаю 2 секунди...\n", getpid(), pid);
    sleep(2); /* Дитина вже завершилася й чекає у стані EXIT_ZOMBIE (Фаза 4) */

    printf("[Батько PID %d] Викликаю waitid() для збирання статусу (Фаза 5)...\n", getpid());

    siginfo_t info;
    memset(&info, 0, sizeof(info));

    /* Використовуємо waitid для отримання детальної структури siginfo_t */
    if (waitid(P_PID, (id_t)pid, &info, WEXITED) == -1) {
        perror("waitid помилка");
        return EXIT_FAILURE;
    }

    if (info.si_code == CLD_EXITED) {
        printf("[Батько PID %d] Дитина PID %d успішно прибрана! Код виходу = %d\n",
               getpid(), info.si_pid, info.si_status);
    } else if (info.si_code == CLD_KILLED || info.si_code == CLD_DUMPED) {
        printf("[Батько PID %d] Дитина PID %d загинула від сигналу %d\n",
               getpid(), info.si_pid, info.si_status);
    }

    printf("[Батько PID %d] task_struct знищено, PID %d вивільнено. Роботу завершено.\n",
           getpid(), pid);
    return EXIT_SUCCESS;
}

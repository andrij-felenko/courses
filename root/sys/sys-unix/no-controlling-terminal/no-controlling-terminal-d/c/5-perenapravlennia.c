/* Приклад класичної демонізації на мові C */
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

int daemonize_traditional(void) {
    /* 1. Перший fork */
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid > 0) _exit(0); /* Батько завершується */

    /* 2. Створення нового сеансу */
    if (setsid() < 0) return -1;

    /* Ігноруємо сигнал SIGHUP при завершенні лідера сеансу */
    signal(SIGHUP, SIG_IGN);

    /* 3. Другий fork */
    pid = fork();
    if (pid < 0) return -1;
    if (pid > 0) _exit(0); /* Лідер сеансу завершується */

    /* 4. Очищення umask і каталогу */
    umask(0);
    if (chdir("/") < 0) return -1;

    /* 5. Перенаправлення дескрипторів 0, 1, 2 на /dev/null */
    int null_fd = open("/dev/null", O_RDWR);
    if (null_fd < 0) return -1;

    dup2(null_fd, STDIN_FILENO);
    dup2(null_fd, STDOUT_FILENO);
    dup2(null_fd, STDERR_FILENO);

    if (null_fd > STDERR_FILENO) {
        close(null_fd);
    }

    return 0;
}

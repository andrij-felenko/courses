/* init.c, друга редакція: підіймає оболонку й не дає системі померти */
#include <sys/mount.h>
#include <sys/wait.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

static void run_wait(char *const argv[])
{
    pid_t p = fork();
    if (p == 0) {
        execv(argv[0], argv);
        _exit(127);
    }
    if (p > 0)
        waitpid(p, NULL, 0);
}

int main(void)
{
    mount("proc",     "/proc", "proc",     0, NULL);
    mount("sysfs",    "/sys",  "sysfs",    0, NULL);
    mount("devtmpfs", "/dev",  "devtmpfs", 0, NULL);

    /* ядро дало нам лише HOME і TERM — решту оточення робимо самі */
    setenv("PATH", "/bin:/sbin:/usr/bin:/usr/sbin", 1);

    /* сотня імен на один файл */
    char *install[] = { "/bin/busybox", "--install", "-s", NULL };
    run_wait(install);

    for (;;) {
        pid_t sh = fork();
        if (sh == 0) {
            setsid();                    /* нова сесія…               */
            ioctl(0, TIOCSCTTY, 1);      /* …і термінал, яким вона керує */
            execl("/bin/sh", "-sh", (char *)NULL);
            _exit(127);
        }

        pid_t r;
        do {
            r = waitpid(-1, NULL, 0);    /* заразом ховаємо всіх сиріт */
        } while (r > 0 && r != sh);

        printf("init: оболонка вийшла, підіймаю нову\n");
    }
}

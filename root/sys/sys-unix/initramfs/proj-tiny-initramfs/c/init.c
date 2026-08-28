/* init.c — найменший PID 1: підняти псевдо-ФС, показатися й не завершитися. */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>

static void mount_one(const char *src, const char *dst,
                      const char *type, unsigned long flags)
{
    if (mkdir(dst, 0755) != 0 && errno != EEXIST)
        printf("[init] mkdir %s: %s\n", dst, strerror(errno));
    if (mount(src, dst, type, flags, NULL) != 0)
        printf("[init] mount %s (%s): %s\n", dst, type, strerror(errno));
    else
        printf("[init] %-8s -> %s\n", type, dst);
}

static void show(const char *path)      /* доказ, що ядро вже відповідає */
{
    char buf[512];
    int fd = open(path, O_RDONLY);
    if (fd < 0) { printf("[init] %s: %s\n", path, strerror(errno)); return; }
    ssize_t n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n > 0) { buf[n] = '\0'; printf("[init] %s: %s", path, buf); }
}

int main(void)
{
    /* Друкувати одразу: якщо машина стане в паніку, скидати буфер буде нікому. */
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("\n[init] PID %d, uid %d — простір користувача живий\n",
           getpid(), getuid());

    mount_one("proc",     "/proc", "proc",     MS_NOSUID | MS_NOEXEC | MS_NODEV);
    mount_one("sysfs",    "/sys",  "sysfs",    MS_NOSUID | MS_NOEXEC | MS_NODEV);
    mount_one("devtmpfs", "/dev",  "devtmpfs", MS_NOSUID);

    show("/proc/cmdline");

    for (;;) {                 /* виходу немає — PID 1 живе до кінця машини */
        int st;
        if (wait(&st) < 0 && errno == ECHILD)
            pause();           /* дітей немає: спимо до наступного сигналу */
    }
}

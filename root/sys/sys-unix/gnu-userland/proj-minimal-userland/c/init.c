/* init.c — увесь простір користувача цієї машини.
   Збірка: gcc -static -Os -o init init.c && strip init */
#include <sys/mount.h>
#include <unistd.h>
#include <stdio.h>

int main(void)
{
    /* службові файлові системи: без них програми сліпі */
    mount("proc",     "/proc", "proc",     0, NULL);
    mount("sysfs",    "/sys",  "sysfs",    0, NULL);
    mount("devtmpfs", "/dev",  "devtmpfs", 0, NULL);

    printf("init: я PID %d, і я тут сам\n", (int)getpid());

    FILE *v = fopen("/proc/version", "r");
    char line[256];
    if (v && fgets(line, sizeof line, v))
        printf("init: ядро каже — %s", line);
    else
        printf("init: /proc не змонтувався, ядро мовчить\n");

    execl("/bin/sh", "sh", (char *)NULL);
    perror("init: /bin/sh");   /* сюди потрапляємо ЛИШЕ при невдачі */

    for (;;)
        pause();               /* вийти звідси не можна */
}

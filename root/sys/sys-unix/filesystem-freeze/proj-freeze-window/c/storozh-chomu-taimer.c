#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/fs.h>          /* FIFREEZE, FITHAW */

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);      /* монотонний час: не стрибне від NTP */
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

/* Сторож. Власний дескриптор відкрито ДО fork і ДО заморожування. */
static pid_t spawn_watchdog(const char *mountpoint, unsigned deadline_ms)
{
    int wfd = open(mountpoint, O_RDONLY | O_DIRECTORY);
    if (wfd < 0) { perror("сторож: open"); return -1; }

    pid_t pid = fork();
    if (pid < 0)  { perror("fork"); close(wfd); return -1; }
    if (pid > 0)  { close(wfd); return pid; }   /* батько сторожевим fd не користується */

    /* --- далі код сторожа: жодного відкриття файлів, жодного stdio --- */
    struct timespec req = { deadline_ms / 1000,
                            (long)(deadline_ms % 1000) * 1000000L }, rem;
    while (nanosleep(&req, &rem) == -1 && errno == EINTR)
        req = rem;                              /* добираємо залишок сну */

    ioctl(wfd, FITHAW, 0);                      /* СПЕРШУ відтаємо… */
    static const char m[] = "СТОРОЖ: дедлайн — файлову систему відтанули\n";
    (void)!write(2, m, sizeof m - 1);           /* …і лише потім говоримо */
    _exit(0);
}

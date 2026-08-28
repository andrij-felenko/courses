#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* Прочитати невеликий файл цілком. Повертає кількість байтів або −1. */
static ssize_t slurp(const char *path, char *buf, size_t cap)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, cap - 1);
    close(fd);
    if (n < 0) return -1;
    buf[n] = '\0';
    return n;
}

/* Стан задачі: 'R', 'S', 'Z'… або 0, якщо запису в /proc уже немає. */
static char proc_state(pid_t pid)
{
    char path[64], buf[512];
    snprintf(path, sizeof path, "/proc/%d/stat", (int)pid);
    if (slurp(path, buf, sizeof buf) < 0) return 0;

    char *p = strrchr(buf, ')');   /* ім'я команди може містити і пробіли, і дужки */
    if (!p) return 0;
    return p[2];                   /* "…) Z 51233 …" — за дужкою пробіл, далі стан */
}

static void sleep_ms(long ms)
{
    struct timespec ts = { ms / 1000, (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);           /* може обірватися сигналом — тут це не шкодить */
}

/* Чекати, доки дитина не стане зомбі. Безпечно рівно тому, що ми — її батько
   і ще не кликали wait: номер нікуди не подінеться. */
static void wait_until_zombie(pid_t pid)
{
    while (proc_state(pid) != 'Z')
        sleep_ms(1);
}

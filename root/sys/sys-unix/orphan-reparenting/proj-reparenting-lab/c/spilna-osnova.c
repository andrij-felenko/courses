#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/wait.h>

static void msleep(long ms)
{
    struct timespec ts;
    ts.tv_sec  = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000L;
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR)
        continue;                  /* ts містить залишок — досипляємо його */
}

/* Ім'я процесу за номером: /proc/<pid>/comm — один рядок без шляху. */
static const char *comm_of(pid_t pid, char *buf, size_t n)
{
    char path[64];
    FILE *f;
    size_t len;

    snprintf(path, sizeof path, "/proc/%d/comm", (int) pid);
    f = fopen(path, "r");
    if (f == NULL || fgets(buf, (int) n, f) == NULL)
        snprintf(buf, n, "?");
    if (f != NULL)
        fclose(f);
    len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n')
        buf[len - 1] = '\0';
    return buf;
}

/* Ядро нікого не будить, коли переписує PPID. Побачити зміну без сигналу
   можна лише одним способом — питати, доки відповідь не стане іншою. */
static pid_t await_reparent(pid_t old, long limit_ms)
{
    pid_t now = getppid();
    long waited = 0;

    while (now == old && waited < limit_ms) {
        msleep(5);
        waited += 5;
        now = getppid();
    }
    return now;
}

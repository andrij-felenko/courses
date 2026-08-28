/* mountprobe.c — вимірює справжній контракт конкретного монтування.
 *   cc -O2 -Wall -Wextra -o mountprobe mountprobe.c
 * на машині A:  ./mountprobe writer /mnt/share 7411
 * на машині B:  ./mountprobe reader /mnt/share hostA 7411
 * шляхи до спільного каталогу на двох машинах МОЖУТЬ бути різні —
 * кожна сторона отримує свій.                                        */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static int  ctl = -1;            /* керувальний сокет */
static char share[PATH_MAX];     /* спільний каталог, як він видний ТУТ */

static double mono(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double) ts.tv_sec + (double) ts.tv_nsec * 1e-9;
}

static void nap_ms(long ms)
{
    struct timespec t = { ms / 1000, (ms % 1000) * 1000000L };
    nanosleep(&t, NULL);
}

/* один статичний буфер — не вживати двічі в одному виразі */
static const char *at(const char *name)
{
    static char p[PATH_MAX];
    snprintf(p, sizeof p, "%s/%s", share, name);
    return p;
}

static const char *secs(double v)      /* -1 означає «не дочекалися» */
{
    static char b[32];
    if (v < 0) snprintf(b, sizeof b, "  > 180");
    else       snprintf(b, sizeof b, "%7.2f", v);
    return b;
}

/* drived.c — служба керування на POSIX-черзі. Збірка: cc -O2 -Wall drived.c -lrt */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <mqueue.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define SLOT 256L        /* найдовше розпорядження плюс запас */

static long read_long(const char *path, long fallback)
{
    FILE *f = fopen(path, "r");
    long v;
    if (!f) return fallback;
    if (fscanf(f, "%ld", &v) != 1) v = fallback;
    fclose(f);
    return v;
}

static long slots_for(long msgsize)
{
    struct rlimit rl;
    long budget, n, ceiling;

    if (getrlimit(RLIMIT_MSGQUEUE, &rl) == -1) return 10;
    budget  = (rl.rlim_cur == RLIM_INFINITY) ? (1L << 20) : (long)(rl.rlim_cur / 2);
    n       = budget / (msgsize + 128);          /* 128 замість ≈96 — свідомий запас */
    ceiling = read_long("/proc/sys/fs/mqueue/msg_max", 10);
    if (n > ceiling) n = ceiling;
    return n < 1 ? 1 : n;
}

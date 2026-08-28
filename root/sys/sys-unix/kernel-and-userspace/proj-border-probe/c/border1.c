/* border1.c — та сама робота, різна кількість перетинів межі.
 * gcc -O2 -o border1 border1.c     запуск: ./border1 <розмір шматка в байтах>
 */
#define _GNU_SOURCE                 /* getrusage і RUSAGE_* без сюрпризів */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/resource.h>

static double tv(const struct timeval *t) { return t->tv_sec + t->tv_usec / 1e6; }

int main(int argc, char **argv)
{
    const size_t TOTAL = 64u << 20;                  /* 64 МіБ у кожному прогоні */
    size_t chunk = (argc > 1) ? strtoul(argv[1], NULL, 0) : 1;
    if (chunk == 0 || TOTAL % chunk) {
        fprintf(stderr, "розмір шматка має націло ділити 64 МіБ\n");
        return 1;
    }

    char *buf = malloc(chunk);
    memset(buf, 'x', chunk);         /* торкаємося сторінок ЗАЗДАЛЕГІДЬ, поза виміром */

    int fd = open("/dev/null", O_WRONLY);
    if (fd < 0) { perror("/dev/null"); return 1; }

    struct rusage r0, r1;
    struct timespec w0, w1;
    getrusage(RUSAGE_SELF, &r0);
    clock_gettime(CLOCK_MONOTONIC, &w0);

    for (size_t done = 0; done < TOTAL; done += chunk)
        if (write(fd, buf, chunk) != (ssize_t) chunk) { perror("write"); return 1; }

    clock_gettime(CLOCK_MONOTONIC, &w1);
    getrusage(RUSAGE_SELF, &r1);

    double wall = (w1.tv_sec - w0.tv_sec) + (w1.tv_nsec - w0.tv_nsec) / 1e9;
    unsigned long calls = TOTAL / chunk;

    printf("шматок %-6zu перетинів %9lu  user %.3f  sys %7.3f  wall %8.4f  %5.0f нс/перетин\n",
           chunk, calls,
           tv(&r1.ru_utime) - tv(&r0.ru_utime),
           tv(&r1.ru_stime) - tv(&r0.ru_stime),
           wall, wall * 1e9 / calls);
    return 0;
}

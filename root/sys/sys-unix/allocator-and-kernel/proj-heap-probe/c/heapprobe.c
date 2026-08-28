/* heapprobe.c — дослід над власною купою */
#define _GNU_SOURCE
#include <fcntl.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define KiB 1024UL
#define MiB (1024UL * KiB)

static char out_buf[8 * 1024];        /* власний буфер stdout: щоб stdio не кликав malloc */

static long proc_status_kib(const char *key)
{
    static char buf[4096];
    ssize_t n;
    char *p;
    int fd = open("/proc/self/status", O_RDONLY);

    if (fd < 0) return -1;
    n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';
    p = strstr(buf, key);
    return p ? strtol(p + strlen(key), NULL, 10) : -1;
}

static long rss_kib(void)   { return proc_status_kib("VmRSS:"); }
static long vsize_kib(void) { return proc_status_kib("VmSize:"); }

static void *brk_now(void) { return sbrk(0); }

/* надрукувати рядок /proc/self/maps, що містить задану адресу */
static void show_map_of(const void *addr)
{
    static char buf[128 * 1024];
    unsigned long want = (unsigned long) addr;
    size_t len = 0;
    ssize_t n;
    char *line;
    int fd = open("/proc/self/maps", O_RDONLY);

    if (fd < 0) return;
    while (len + 1 < sizeof buf && (n = read(fd, buf + len, sizeof buf - 1 - len)) > 0)
        len += (size_t) n;
    close(fd);
    buf[len] = '\0';

    for (line = buf; line && *line; ) {
        char *end = strchr(line, '\n');
        unsigned long lo = 0, hi = 0;

        if (end) *end = '\0';
        if (sscanf(line, "%lx-%lx", &lo, &hi) == 2 && want >= lo && want < hi)
            printf("        %s   (%lu КіБ)\n", line, (hi - lo) / KiB);
        line = end ? end + 1 : NULL;
    }
}

static void *xmalloc(size_t n)
{
    void *p = malloc(n);
    if (!p) { fprintf(stderr, "malloc(%zu) не вдався\n", n); exit(1); }
    return p;
}

/* сховати покажчик від оптимізатора (навіщо — у пастках наприкінці) */
static void *opaque(void *p)
{
    __asm__ volatile ("" : "+r"(p) : : "memory");
    return p;
}

static double now_s(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double) t.tv_sec + (double) t.tv_nsec / 1e9;
}

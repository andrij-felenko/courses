/* faultlab.c — вимірювання сторінкових збоїв.
   Збірка:  cc -O2 -std=gnu11 -o faultlab faultlab.c            */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/stat.h>

#ifndef MADV_POPULATE_WRITE           /* з'явилося в Linux 5.14 */
#define MADV_POPULATE_WRITE 23
#endif

#define PGSZ   4096UL
#define ANON   (1024UL * 1024 * 1024)      /* 1 ГіБ анонімної пам'яті */
#define FSIZE  (256UL  * 1024 * 1024)      /* 256 МіБ файлу           */

/* Куди зливати прочитане, щоб компілятор не викинув самі читання. */
volatile unsigned long sink;

struct mark { double t; unsigned long minf, majf; };

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void counters(unsigned long *minf, unsigned long *majf)
{
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);        /* RUSAGE_THREAD — якщо потоків кілька */
    *minf = ru.ru_minflt;
    *majf = ru.ru_majflt;
}

static void mark_begin(struct mark *m)  /* час беремо ОСТАННІМ  */
{
    counters(&m->minf, &m->majf);
    m->t = now();
}

static void mark_end(const struct mark *m, const char *what)
{
    double dt = now() - m->t;           /* час беремо ПЕРШИМ    */
    unsigned long minf, majf;
    counters(&minf, &majf);
    printf("  %-32s %9.3f мс   minflt +%-8lu majflt +%lu\n",
           what, dt * 1e3, minf - m->minf, majf - m->majf);
}

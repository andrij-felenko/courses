/* rtloop.c — періодичний потік на SCHED_FIFO з вимірюванням запізнення.
 * gcc -O2 -Wall -pthread -Wl,-z,now -o rtloop rtloop.c                     */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <malloc.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

#define PERIOD_NS    1000000L                /* 1 кГц                        */
#define RUN_SECONDS  60                      /* для серйозного виміру — години */
#define ITERATIONS   ((uint64_t)RUN_SECONDS * 1000000000ULL / PERIOD_NS)
#define RT_PRIORITY  60
#define STACK_BYTES  (512 * 1024)
#define PREFAULT     (256 * 1024)
#define BUCKETS      2000                    /* кошики по 1 мкс, стеля 2 мс   */

struct stats {
    uint32_t hist[BUCKETS];
    uint64_t samples, sum_ns, worst_ns;
    long     minflt_before, minflt_after;
};

static inline uint64_t ns_of(const struct timespec *t)
{
    return (uint64_t)t->tv_sec * 1000000000ULL + (uint64_t)t->tv_nsec;
}

static inline void ts_add_ns(struct timespec *t, long ns)
{
    t->tv_nsec += ns;
    while (t->tv_nsec >= 1000000000L) { t->tv_nsec -= 1000000000L; t->tv_sec++; }
}

/* Заходимо вглиб стека й торкаємось кожної сторінки. volatile — щоб
 * оптимізатор не викинув запис у масив, який більше ніде не читають.       */
static void prefault_stack(void)
{
    volatile unsigned char deep[PREFAULT];
    long page = sysconf(_SC_PAGESIZE);
    for (size_t i = 0; i < PREFAULT; i += (size_t)page)
        deep[i] = 0;
}

/* Поки цей дескриптор відкритий, ядро не пускає процесори в глибокий сон.
 * Закриття скасовує прохання, тому дескриптор НЕ закриваємо.               */
static int deny_deep_idle(void)
{
    int32_t target_us = 0;
    int fd = open("/dev/cpu_dma_latency", O_WRONLY);
    if (fd >= 0 && write(fd, &target_us, sizeof target_us) != sizeof target_us) {
        close(fd);
        fd = -1;
    }
    return fd;
}

static void payload(uint64_t k, volatile double *sink)
{
    double x = 1.0 + (double)(k & 0xff);
    for (int i = 0; i < 400; i++) x = x * 1.0000001 + 1e-9;
    *sink = x;                               /* тут була б корисна робота     */
}

static void *rt_loop(void *arg)
{
    struct stats *st = arg;
    struct timespec next, woke;
    struct rusage  ru;
    volatile double sink = 0.0;

    prefault_stack();                        /* стек ЦЬОГО потоку            */

    getrusage(RUSAGE_THREAD, &ru);
    st->minflt_before = ru.ru_minflt;

    clock_gettime(CLOCK_MONOTONIC, &next);
    ts_add_ns(&next, PERIOD_NS);

    for (uint64_t k = 0; k < ITERATIONS; k++) {
        int rc;
        do {
            rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
        } while (rc == EINTR);               /* сам не перезапуститься       */
        if (rc != 0) break;

        clock_gettime(CLOCK_MONOTONIC, &woke);

        int64_t late = (int64_t)(ns_of(&woke) - ns_of(&next));
        if (late < 0) late = 0;

        size_t b = (size_t)(late / 1000);
        if (b >= BUCKETS) b = BUCKETS - 1;
        st->hist[b]++;
        st->sum_ns += (uint64_t)late;
        if ((uint64_t)late > st->worst_ns) st->worst_ns = (uint64_t)late;
        st->samples++;

        payload(k, &sink);

        ts_add_ns(&next, PERIOD_NS);         /* сітка, а не «від зараз»      */
    }

    getrusage(RUSAGE_THREAD, &ru);
    st->minflt_after = ru.ru_minflt;
    return NULL;
}

static void report(const struct stats *st)
{
    uint64_t seen = 0, p99 = 0, p9999 = 0;

    if (st->samples == 0) { printf("жодного зразка\n"); return; }

    for (size_t b = 0; b < BUCKETS; b++) {
        seen += st->hist[b];
        if (!p99   && seen * 100ULL   >= st->samples * 99ULL)   p99   = b + 1;
        if (!p9999 && seen * 10000ULL >= st->samples * 9999ULL) p9999 = b + 1;
    }
    printf("зразків          : %llu\n",      (unsigned long long)st->samples);
    printf("середнє          : %.1f мкс\n",  st->sum_ns / 1000.0 / st->samples);
    printf("p99              : %llu мкс\n",  (unsigned long long)p99);
    printf("p99.99           : %llu мкс\n",  (unsigned long long)p9999);
    printf("максимум         : %.1f мкс\n",  st->worst_ns / 1000.0);
    printf("сторінкових збоїв: %ld\n",       st->minflt_after - st->minflt_before);
}

int main(void)
{
    struct stats *st = malloc(sizeof *st);
    pthread_attr_t attr;
    struct sched_param param = { .sched_priority = RT_PRIORITY };
    pthread_t th;
    int rc;

    if (!st) return 1;
    memset(st, 0, sizeof *st);               /* торкаємось усіх сторінок     */

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) { perror("mlockall"); return 1; }
    mallopt(M_TRIM_THRESHOLD, -1);
    mallopt(M_MMAP_MAX, 0);
    deny_deep_idle();                        /* дескриптор лишається живим   */

    pthread_attr_init(&attr);
    pthread_attr_setstacksize(&attr, STACK_BYTES);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    pthread_attr_setschedparam(&attr, &param);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);  /* без цього
                                   два попередні рядки не роблять нічого     */

    rc = pthread_create(&th, &attr, rt_loop, st);
    if (rc != 0) { fprintf(stderr, "pthread_create: %s\n", strerror(rc)); return 1; }

    pthread_join(th, NULL);
    report(st);
    return 0;
}

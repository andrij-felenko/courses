/* latency.c — вимірювач затримки планування.
   збірка:  cc -O2 -Wall -pthread latency.c -o latency
   запуск:  sudo ./latency [період_мкс] [секунд] [ядро]            */

#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define NSEC    1000000000L
#define BUCKETS 2000                    /* кошик = 1 мкс, отже 0…1999 мкс */
#define WARM    (256 * 1024)            /* скільки стека розігріти */

static long period_ns = 200 * 1000;     /* 200 мкс */
static long run_sec   = 600;
static int  cpu_id    = 3;

static unsigned long *hist;             /* гістограма запізнень */
static unsigned long  over;             /* обертів поза межами гістограми */
static unsigned long  total;
static long           worst;            /* найгірше запізнення, мкс */

static void ts_add_ns(struct timespec *t, long ns)
{
    t->tv_nsec += ns;
    while (t->tv_nsec >= NSEC) {
        t->tv_nsec -= NSEC;
        t->tv_sec++;
    }
}

static long ts_sub_ns(const struct timespec *a, const struct timespec *b)
{
    return (a->tv_sec - b->tv_sec) * NSEC + (a->tv_nsec - b->tv_nsec);
}

/* доторкнутися до кожної сторінки стека, поки нам не горить */
static void warm_stack(void)
{
    unsigned char pad[WARM];

    memset(pad, 0, sizeof pad);
    __asm__ volatile ("" :: "r"(pad) : "memory");   /* щоб не викинув компілятор */
}

static void *meter(void *arg)
{
    struct timespec next, now;
    long i, cycles = run_sec * (NSEC / period_ns);
    long late_us;

    (void)arg;
    warm_stack();

    clock_gettime(CLOCK_MONOTONIC, &next);
    next.tv_nsec = 0;
    next.tv_sec += 1;                   /* сітку починаємо з рівної секунди */

    for (i = 0; i < cycles; i++) {
        /* НАСТУПНИЙ момент — від сітки, а не від «зараз» */
        ts_add_ns(&next, period_ns);

        /* сигнал перервав сон — спимо далі ДО ТОГО САМОГО моменту;
           з TIMER_ABSTIME залишок непотрібний, ціль незмінна */
        while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL) == EINTR)
            ;

        clock_gettime(CLOCK_MONOTONIC, &now);

        late_us = ts_sub_ns(&now, &next) / 1000;
        if (late_us < 0)                /* прокинулися раніше — рідко, але буває */
            late_us = 0;
        if (late_us > worst)
            worst = late_us;
        if (late_us < BUCKETS)
            hist[late_us]++;
        else
            over++;
        total++;
    }
    return NULL;
}

int main(int argc, char **argv)
{
    struct sched_param sp = { .sched_priority = 80 };
    pthread_attr_t attr;
    pthread_t th;
    cpu_set_t set;
    unsigned long long acc = 0;
    long i, p50 = -1, p999 = -1, p99999 = -1;

    if (argc > 1) period_ns = atol(argv[1]) * 1000;
    if (argc > 2) run_sec   = atol(argv[2]);
    if (argc > 3) cpu_id    = atoi(argv[3]);

    /* мовчки пропустити помилку тут — значить збрехати собі в усіх числах нижче */
    if (mlockall(MCL_CURRENT | MCL_FUTURE)) {
        perror("mlockall");
        return 1;
    }

    hist = malloc(BUCKETS * sizeof *hist);
    if (!hist) {
        perror("malloc");
        return 1;
    }
    for (i = 0; i < BUCKETS; i++)       /* доторк до КОЖНОЇ сторінки ДО циклу */
        hist[i] = 0;

    CPU_ZERO(&set);
    CPU_SET(cpu_id, &set);

    pthread_attr_init(&attr);
    pthread_attr_setstacksize(&attr, 1024 * 1024);
    /* без EXPLICIT_SCHED політику й пріоритет успадкують від нас, а наші
       три рядки нижче ядро просто проігнорує — мовчки */
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    pthread_attr_setschedparam(&attr, &sp);
    pthread_attr_setaffinity_np(&attr, sizeof set, &set);

    if (pthread_create(&th, &attr, meter, NULL)) {
        fputs("pthread_create: немає прав на SCHED_FIFO?\n", stderr);
        return 1;
    }
    pthread_join(th, NULL);

    for (i = 0; i < BUCKETS; i++) {
        if (!hist[i])
            continue;
        acc += hist[i];
        if (p50    < 0 && acc * 2      >= (unsigned long long)total)
            p50 = i;
        if (p999   < 0 && acc * 1000   >= (unsigned long long)total * 999)
            p999 = i;
        if (p99999 < 0 && acc * 100000 >= (unsigned long long)total * 99999)
            p99999 = i;
        printf("%5ld мкс %10lu\n", i, hist[i]);
    }
    printf("\nобертів %lu, поза гістограмою %lu\n", total, over);
    printf("медіана %ld мкс · 99.9%% %ld мкс · 99.999%% %ld мкс · максимум %ld мкс\n",
           p50, p999, p99999, worst);
    return 0;
}

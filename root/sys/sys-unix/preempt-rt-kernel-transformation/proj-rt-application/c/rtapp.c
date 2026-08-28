/* rtapp.c — періодичний контур керування 1 кГц під PREEMPT_RT.
 * gcc -O2 -Wall -pthread -Wl,-z,now -o rtapp rtapp.c                        */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <malloc.h>
#include <pthread.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define PERIOD_NS   1000000L                 /* 1 кГц                        */
#define ROTATE      1000                     /* обмін кошиками раз на секунду */
#define BUCKETS     2048                     /* кошики по 1 мкс              */
#define STACK_WARM  (256 * 1024)
#define HEAP_WARM   (4 * 1024 * 1024)

struct bin {
    uint32_t hist[BUCKETS];
    uint64_t n, sum_ns, worst_ns, overrun;
};

static struct bin       bins[2];
static struct bin      *hot   = &bins[0];    /* пише лише гарячий потік      */
static struct bin      *ready = NULL;        /* повний, чекає на звіт        */
static struct bin      *spare = &bins[1];    /* порожній, чекає на обмін     */
static pthread_mutex_t  m;                   /* PTHREAD_PRIO_INHERIT         */
static int              rt_prio;

static int irq_thread_prio(const char *needle);      /* тіло — у фрагменті вище */

static inline uint64_t ns_of(const struct timespec *t)
{
    return (uint64_t)t->tv_sec * 1000000000ULL + (uint64_t)t->tv_nsec;
}

static inline void ts_add_ns(struct timespec *t, long ns)
{
    t->tv_nsec += ns;
    while (t->tv_nsec >= 1000000000L) { t->tv_nsec -= 1000000000L; t->tv_sec++; }
}

/* Стек ЦЬОГО потоку заселяється ліниво — заходимо вглиб і торкаємось усього.
 * volatile — щоб оптимізатор не викинув запис у масив, який ніде не читають. */
static void warm_stack(void)
{
    volatile unsigned char deep[STACK_WARM];
    long page = sysconf(_SC_PAGESIZE);
    size_t i;
    for (i = 0; i < STACK_WARM; i += (size_t)page) deep[i] = 0;
}

static void control_step(uint64_t k, volatile double *out)
{
    double x = 1.0 + (double)(k & 0xff);     /* тут була б справжня поправка  */
    int i;
    for (i = 0; i < 400; i++) x = x * 1.0000001 + 1e-9;
    *out = x;
}

static void *rt_loop(void *unused)
{
    struct sched_param param = { .sched_priority = rt_prio };
    struct timespec next, woke;
    volatile double out = 0.0;
    uint64_t k;

    (void)unused;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {   /* 0 — цей потік  */
        perror("sched_setscheduler");
        exit(1);
    }
    warm_stack();

    clock_gettime(CLOCK_MONOTONIC, &next);
    ts_add_ns(&next, PERIOD_NS);

    for (k = 0; ; k++) {
        int rc;
        int64_t late;
        size_t b;

        do {
            rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
        } while (rc == EINTR);               /* сам не перезапуститься        */
        if (rc != 0) break;

        clock_gettime(CLOCK_MONOTONIC, &woke);
        late = (int64_t)(ns_of(&woke) - ns_of(&next));
        if (late < 0) late = 0;

        b = (size_t)(late / 1000);
        if (b >= BUCKETS) b = BUCKETS - 1;
        hot->hist[b]++;
        hot->sum_ns += (uint64_t)late;
        hot->n++;
        if ((uint64_t)late > hot->worst_ns) hot->worst_ns = (uint64_t)late;
        if (late >= PERIOD_NS) hot->overrun++;            /* такт пропущено   */

        control_step(k, &out);

        if ((k + 1) % ROTATE == 0) {         /* єдиний дотик до спільного     */
            pthread_mutex_lock(&m);
            if (spare != NULL) { ready = hot; hot = spare; spare = NULL; }
            pthread_mutex_unlock(&m);
        }
        ts_add_ns(&next, PERIOD_NS);         /* сітка, а не «ще мілісекунда»  */
    }
    return NULL;
}

static void report(const struct bin *b)
{
    uint64_t seen = 0, p99 = 0, p9999 = 0;
    size_t i;

    if (b->n == 0) return;
    for (i = 0; i < BUCKETS; i++) {
        seen += b->hist[i];
        if (!p99   && seen * 100ULL   >= b->n * 99ULL)   p99   = i + 1;
        if (!p9999 && seen * 10000ULL >= b->n * 9999ULL) p9999 = i + 1;
    }
    printf("n=%llu  сер=%.1f  p99=%llu  p99.99=%llu  макс=%.1f мкс  пропущено=%llu\n",
           (unsigned long long)b->n, b->sum_ns / 1000.0 / b->n,
           (unsigned long long)p99, (unsigned long long)p9999,
           b->worst_ns / 1000.0, (unsigned long long)b->overrun);
    fflush(stdout);
}

static void *reporter(void *unused)
{
    (void)unused;
    for (;;) {
        struct bin *b;
        sleep(1);

        pthread_mutex_lock(&m);
        b = ready; ready = NULL;
        pthread_mutex_unlock(&m);

        if (b == NULL) continue;
        report(b);                            /* друк — уже поза замком       */
        memset(b, 0, sizeof *b);
        pthread_mutex_lock(&m);
        spare = b;
        pthread_mutex_unlock(&m);
    }
    return NULL;
}

static void warn_throttling(void)
{
    long long runtime = -1, period = 1000000;
    FILE *f;
    if ((f = fopen("/proc/sys/kernel/sched_rt_runtime_us", "r")) != NULL) {
        if (fscanf(f, "%lld", &runtime) != 1) runtime = -1;
        fclose(f);
    }
    if ((f = fopen("/proc/sys/kernel/sched_rt_period_us", "r")) != NULL) {
        if (fscanf(f, "%lld", &period) != 1) period = 1000000;
        fclose(f);
    }
    if (runtime >= 0)
        fprintf(stderr, "запобіжник живий: %lld мкс із %lld — за їх вичерпання "
                        "буде примусова пауза %lld мкс\n",
                runtime, period, period - runtime);
}

int main(int argc, char **argv)
{
    pthread_mutexattr_t ma;
    pthread_attr_t      ta;
    pthread_t           th_rt, th_rep;
    const char         *device = (argc > 1) ? argv[1] : "eth0";
    void               *warm;
    int                 irq_prio;

    irq_prio = irq_thread_prio(device);
    if (irq_prio < 0) {
        fprintf(stderr, "потоку irq/*%s* не знайдено: ядро без PREEMPT_RT "
                        "або хибна назва пристрою\n", device);
        return 1;
    }
    rt_prio = irq_prio - 1;                  /* свідомо ПІД своїм джерелом    */
    fprintf(stderr, "irq/%s має %d, цикл бере %d\n", device, irq_prio, rt_prio);
    warn_throttling();

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) { perror("mlockall"); return 1; }
    mallopt(M_TRIM_THRESHOLD, -1);           /* не віддавати звільнене ядру   */
    mallopt(M_MMAP_MAX, 0);                  /* не брати великі шматки mmap-ом */
    if ((warm = malloc(HEAP_WARM)) != NULL) { memset(warm, 0, HEAP_WARM); free(warm); }
    memset(bins, 0, sizeof bins);            /* торкаємось обох кошиків       */

    pthread_mutexattr_init(&ma);
    if (pthread_mutexattr_setprotocol(&ma, PTHREAD_PRIO_INHERIT) != 0) {
        fprintf(stderr, "успадкування пріоритету недоступне\n");
        return 1;
    }
    pthread_mutex_init(&m, &ma);

    pthread_attr_init(&ta);
    pthread_attr_setstacksize(&ta, STACK_WARM + 128 * 1024);
    pthread_create(&th_rt, &ta, rt_loop, NULL);
    pthread_create(&th_rep, NULL, reporter, NULL);   /* лишається звичайним   */
    pthread_join(th_rt, NULL);
    return 0;
}

/* share.c — хто скільки процесора дістає й якими порціями.
   збірка:  cc -O2 -Wall -pthread share.c -o share
   запуск:  ./share [номер ядра]        (звичайних прав досить)  */

#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>
#include <linux/sched/types.h>          /* struct sched_attr */

#define WINDOW_SEC 4
#define WS_BYTES   (256 * 1024)         /* робоча множина одного працівника */
#define CHUNK      1024                 /* кроків між оновленнями лічильника */

struct worker {
    const char        *name;
    int                nice;            /* який nice поставити задачі */
    unsigned long long slice;           /* прохання про відрізок, нс; 0 — типовий */

    pid_t              tid;
    pthread_t          th;
    _Atomic unsigned long long steps;

    double             cpu0, cpu1;      /* спожитий час, с */
    unsigned long long wait0, wait1;    /* час у черзі готових, нс */
    unsigned long long vis0, vis1;      /* скільки разів сідала на процесор */
    unsigned long long step0, step1;
};

/* ДОСЛІД 1: чи дають ваги обіцяні частки */
static struct worker plan[] = {
    { .name = "A", .nice = 0, .slice = 0 },
    { .name = "B", .nice = 0, .slice = 0 },
    { .name = "C", .nice = 5, .slice = 0 },
};
#define N ((int)(sizeof plan / sizeof plan[0]))

/* sched_prio_to_weight[] з ядра; індекс — nice + 20 */
static const int weight[40] = {
    88761, 71755, 56483, 46273, 36291,      /* nice -20 … -16 */
    29154, 23254, 18705, 14949, 11916,
     9548,  7620,  6100,  4904,  3906,
     3121,  2501,  1991,  1586,  1277,
     1024,   820,   655,   526,   423,      /* nice   0 …   4 */
      335,   272,   215,   172,   137,
      110,    87,    70,    56,    45,
       36,    29,    23,    18,    15,      /* nice  15 …  19 */
};

static atomic_int        stop;
static pthread_barrier_t ready;
static int               field;             /* ядро, на якому робимо тісноту */

static int pin(pid_t tid, int cpu)
{
    cpu_set_t set;

    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    return sched_setaffinity(tid, sizeof set, &set);
}

/* прохання про довжину відрізка: читаємо все, що вже стоїть, міняємо одне
   поле й пишемо назад — інакше затремо власний nice нулем */
static int ask_slice(pid_t tid, unsigned long long ns)
{
    struct sched_attr a;

    memset(&a, 0, sizeof a);
    if (syscall(SYS_sched_getattr, tid, &a, sizeof a, 0u))
        return -1;
    a.size          = sizeof a;
    a.sched_runtime = ns;
    if (syscall(SYS_sched_setattr, tid, &a, 0u))
        return -1;

    /* доказ — не код повернення, а те, що ядро віддає назад */
    memset(&a, 0, sizeof a);
    if (syscall(SYS_sched_getattr, tid, &a, sizeof a, 0u))
        return -1;
    return a.sched_runtime == ns ? 0 : -1;
}

/* /proc/<tid>/schedstat: спожито нс, чекано в черзі нс, скільки разів сідала */
static int read_schedstat(pid_t tid, unsigned long long *wait,
                          unsigned long long *vis)
{
    char path[64];
    unsigned long long run;
    FILE *f;
    int n;

    snprintf(path, sizeof path, "/proc/self/task/%d/schedstat", (int)tid);
    if (!(f = fopen(path, "r")))
        return -1;
    n = fscanf(f, "%llu %llu %llu", &run, wait, vis);
    fclose(f);
    return n == 3 ? 0 : -1;
}

/* спожитий час чужого потоку — те саме sum_exec_runtime, лише годинником */
static double cpu_seconds(pthread_t th)
{
    struct timespec ts;
    clockid_t cid;

    if (pthread_getcpuclockid(th, &cid) || clock_gettime(cid, &ts))
        return 0.0;
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void *worker(void *arg)
{
    struct worker *w = arg;
    unsigned n = WS_BYTES / sizeof(unsigned), i, p = 0, *ring;
    unsigned long long r, done = 0;

    w->tid = syscall(SYS_gettid);
    if (pin(w->tid, field))
        perror("sched_setaffinity");
    if (setpriority(PRIO_PROCESS, w->tid, w->nice))
        perror("setpriority");
    if (w->slice && ask_slice(w->tid, w->slice))
        fprintf(stderr, "%s: ядро не взяло прохання про відрізок\n", w->name);

    /* кільце випадкового обходу: адреса кожного кроку відома лише після
       попереднього, тож попередня вибірка безсила, а після витіснення
       робочу множину доводиться набирати в кеш наново */
    ring = malloc((size_t)n * sizeof *ring);
    for (i = 0; i < n; i++)
        ring[i] = i;
    r = 0x9e3779b97f4a7c15ULL ^ (unsigned long long)w->tid;
    for (i = n - 1; i > 0; i--) {           /* перемішування Саттоло: один цикл */
        unsigned j, t;

        r ^= r << 13; r ^= r >> 7; r ^= r << 17;
        j = (unsigned)(r % i);
        t = ring[i]; ring[i] = ring[j]; ring[j] = t;
    }

    pthread_barrier_wait(&ready);

    /* у циклі — жодного системного виклику: задача віддає процесор лише
       тоді, коли його відберуть */
    while (!atomic_load_explicit(&stop, memory_order_relaxed)) {
        for (i = 0; i < CHUNK; i++)
            p = ring[p];
        done += CHUNK;
        atomic_store_explicit(&w->steps, done, memory_order_relaxed);
    }
    free(ring);
    return (void *)(unsigned long)p;        /* щоб обхід не викинули */
}

int main(int argc, char **argv)
{
    struct timespec win = { WINDOW_SEC, 0 };
    unsigned long long wsum = 0;
    double total = 0.0, best = 0.0;
    int i, empty = 1;

    field = (argc > 1) ? atoi(argv[1]) : 3;
    if (pin(0, field ? 0 : 1))              /* вимірювач — геть із поля досліду */
        perror("sched_setaffinity(main)");

    pthread_barrier_init(&ready, NULL, N + 1);
    for (i = 0; i < N; i++)
        if (pthread_create(&plan[i].th, NULL, worker, &plan[i])) {
            perror("pthread_create");
            return 1;
        }

    pthread_barrier_wait(&ready);           /* усі налаштовані й стоять на старті */
    for (i = 0; i < N; i++) {
        plan[i].cpu0  = cpu_seconds(plan[i].th);
        plan[i].step0 = atomic_load(&plan[i].steps);
        read_schedstat(plan[i].tid, &plan[i].wait0, &plan[i].vis0);
    }

    nanosleep(&win, NULL);                  /* вимірювач спить — часу не їсть */

    for (i = 0; i < N; i++) {
        plan[i].cpu1  = cpu_seconds(plan[i].th);
        plan[i].step1 = atomic_load(&plan[i].steps);
        read_schedstat(plan[i].tid, &plan[i].wait1, &plan[i].vis1);
    }
    atomic_store(&stop, 1);
    for (i = 0; i < N; i++)
        pthread_join(plan[i].th, NULL);

    for (i = 0; i < N; i++) {
        double sec  = plan[i].cpu1 - plan[i].cpu0;
        double rate = (double)(plan[i].step1 - plan[i].step0) / sec;

        total += sec;
        wsum  += (unsigned)weight[plan[i].nice + 20];
        if (rate > best)
            best = rate;
        if (plan[i].vis1 - plan[i].vis0)
            empty = 0;
    }

    printf("ядро %d, вікно %d с, задач %d\n\n", field, WINDOW_SEC, N);
    puts("задача nice  вага  спожито,с  частка  очікув.   візитів  порція,мс"
         "  чекання,мс   робота");
    for (i = 0; i < N; i++) {
        struct worker *w = &plan[i];
        double sec = w->cpu1 - w->cpu0;
        unsigned long long vis = w->vis1 - w->vis0;

        printf("%-6s %4d %5d %10.3f %7.2f%% %7.2f%% %9llu %10.3f %11.3f %8.2f\n",
               w->name, w->nice, weight[w->nice + 20],
               sec, 100.0 * sec / total,
               100.0 * weight[w->nice + 20] / wsum,
               vis,
               vis ? sec * 1e3 / vis : 0.0,
               vis ? (double)(w->wait1 - w->wait0) / 1e6 / vis : 0.0,
               ((double)(w->step1 - w->step0) / sec) / best);
    }
    if (empty)
        puts("\nвізити й чекання порожні — увімкніть облік:"
             "  sudo sysctl -w kernel.sched_schedstats=1");
    return 0;
}

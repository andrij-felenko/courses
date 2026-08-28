static volatile int64_t sink;    /* сюди складаємо результат, щоб він був потрібен */

#define OPAQUE(v) __asm__ __volatile__("" : "+r"(v))   /* GCC / Clang */

typedef int64_t (*probe_fn)(void);

static int64_t probe_empty(void)    { return 1; }

static int64_t probe_vdso(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return to_ns(&t);
}

static int64_t probe_coarse(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC_COARSE, &t);
    return to_ns(&t);
}

static int64_t probe_syscall(void)
{
    struct timespec t;
    /* Обхід vDSO: просимо ядро напряму, номером системного виклику.
       На 32-бітних архітектурах із 64-бітним часом потрібен інший вхід. */
#ifdef SYS_clock_gettime64
    if (sizeof(time_t) == 8)
        syscall(SYS_clock_gettime64, CLOCK_MONOTONIC, &t);
    else
#endif
        syscall(SYS_clock_gettime, CLOCK_MONOTONIC, &t);
    return to_ns(&t);
}

__attribute__((noinline))
static double cost_ns(probe_fn fn, unsigned iters)
{
    struct timespec t0, t1;

    OPAQUE(fn);                  /* компілятор більше не знає, кого ми кличемо */

    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (unsigned i = 0; i < iters; i++)
        sink = fn();
    clock_gettime(CLOCK_MONOTONIC, &t1);

    return (double)(to_ns(&t1) - to_ns(&t0)) / iters;
}

static double best_cost(probe_fn fn, unsigned iters, unsigned rounds)
{
    double best = 1e18;
    for (unsigned r = 0; r < rounds; r++) {
        double c = cost_ns(fn, iters);
        if (c < best) best = c;    /* шум тільки додає — істина знизу */
    }
    return best;
}

static void pin_to_current_cpu(void)
{
    cpu_set_t set;
    int cpu = sched_getcpu();

    if (cpu < 0) return;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0)
        fprintf(stderr, "прив'язка до ядра %d не вдалася: %s\n", cpu, strerror(errno));
    else
        printf("вимір прив'язано до ядра %d\n", cpu);
}

static void show_cost(void)
{
    const unsigned ITERS = 200000, ROUNDS = 9;
    double base   = best_cost(probe_empty,   ITERS, ROUNDS);
    double vdso   = best_cost(probe_vdso,    ITERS, ROUNDS);
    double coarse = best_cost(probe_coarse,  ITERS, ROUNDS);
    double sysc   = best_cost(probe_syscall, ITERS, ROUNDS);

    printf("порожній цикл (віднімається) %8.1f нс\n", base);
    printf("CLOCK_MONOTONIC              %8.1f нс\n", vdso   - base);
    printf("CLOCK_MONOTONIC_COARSE       %8.1f нс\n", coarse - base);
    printf("той самий запит як syscall() %8.1f нс\n", sysc   - base);
}

static uint64_t now_ns(void)
{
    struct timespec t;

    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ULL + (uint64_t)t.tv_nsec;
}

/* Один байт у задану сторінку разом із двома читаннями годинника.
   volatile — щоб запис не викинули; бар'єри — щоб його не переставили
   за межі виміру. */
static uint64_t poke(unsigned char *base, unsigned long page_idx)
{
    volatile unsigned char *p = base + page_idx * PAGE + 64;
    uint64_t t0, t1;

    __asm__ __volatile__("" ::: "memory");
    t0 = now_ns();
    *p ^= 0x5A;
    t1 = now_ns();
    __asm__ __volatile__("" ::: "memory");
    return t1 - t0;
}

static unsigned long minflt(void)
{
    char buf[1024], *p;
    unsigned long v = 0;
    ssize_t n;
    int fd = open("/proc/self/stat", O_RDONLY);

    if (fd < 0) return 0;
    n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0) return 0;
    buf[n] = '\0';

    /* Друге поле — ім'я програми в дужках, і в ньому бувають і пробіли,
       і самі дужки. Тому шукаємо ОСТАННЮ ')', а не рахуємо поля зліва.
       Далі: state ppid pgrp session tty_nr tpgid flags minflt. */
    if ((p = strrchr(buf, ')')) == NULL) return 0;
    sscanf(p + 1, " %*c %*d %*d %*d %*d %*d %*u %lu", &v);
    return v;
}

static int cmp_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;

    return (x > y) - (x < y);
}

static void report(const char *name, uint64_t *v, size_t n)
{
    qsort(v, n, sizeof *v, cmp_u64);
    printf("%s  %8.3f мкс %8.3f мкс %8.3f мкс\n", name,
           v[n / 2] / 1000.0, v[0] / 1000.0, v[(size_t)(n * 0.9)] / 1000.0);
}

static void pin_to_current_cpu(void)
{
    cpu_set_t set;
    int cpu = sched_getcpu();

    if (cpu < 0) return;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set) == 0)
        printf("вимір прив'язано до ядра %d\n", cpu);
}

static void measure(unsigned char *merged, unsigned char *plain)
{
    uint64_t *tm = malloc(NPROBE * sizeof *tm);
    uint64_t *tp = malloc(NPROBE * sizeof *tp);
    unsigned long i, before, after;
    double med_m, med_p;

    if (!tm || !tp) { perror("malloc"); exit(1); }
    before = minflt();

    for (i = 0; i < NPROBE; i++) {
        unsigned long idx = (i * STRIDE) % NPAGES;   /* однаковий порядок обходу
                                                        для обох ділянок */
        tp[i] = poke(plain,  idx);
        tm[i] = poke(merged, idx);
    }
    after = minflt();

    printf("\n── ціна одного байта (%lu сторінок кожного роду) ──\n", NPROBE);
    puts("                медіана    мінімум     90-й %");
    report("незлита (C)", tp, NPROBE);
    report("злита   (A)", tm, NPROBE);

    med_p = tp[NPROBE / 2] / 1000.0;
    med_m = tm[NPROBE / 2] / 1000.0;
    printf("різниця      %8.3f мкс  (у %.1f раза)\n", med_m - med_p, med_m / med_p);
    printf("малих збоїв: %s → %s  (+%lu на %lu записів у злиті сторінки)\n",
           sp(before), sp(after), after - before, NPROBE);

    free(tm);
    free(tp);
}

int main(void)
{
    unsigned char *r[3];

    if (ksm_get("run") < 0) {
        fprintf(stderr, "немає " KSM " — ядро зібране без CONFIG_KSM\n");
        return 1;
    }
    take_knobs();
    pin_to_current_cpu();

    r[0] = new_region();  fill(r[0], 0x51ab000000000001ULL);   /* A — близнюк */
    r[1] = new_region();  fill(r[1], 0x51ab000000000001ULL);   /* B — близнюк */
    r[2] = new_region();  fill(r[2], 0x9e0c000000000001ULL);   /* C — контроль */

    snapshot("до сканування", r);
    wait_scans(3);
    snapshot("після трьох повних проходів", r);

    measure(r[0], r[2]);

    wait_scans(1);
    snapshot("після виміру й ще одного проходу", r);
    return 0;
}

static volatile uint64_t sink;      /* запис у volatile викинути не можна */

/* Порожня проба — це тло: ціна самого циклу й переходу ланцюгом. */
static void probe_idle(void) { }

/* Найдешевший системний виклик, який тільки є: ядро віддає число,
   що вже лежить у структурі задачі. Кличемо через syscall(), щоб між
   нами й ядром не стояла обгортка libc, здатна закешувати відповідь. */
static void probe_getppid(void)
{
    sink += (uint64_t)syscall(SYS_getppid);
}

/* Той самий сенс двома шляхами. Перший бере час із vDSO і межі не
   перетинає взагалі; другий іде справжнім системним викликом. */
static void probe_vdso(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    sink += (uint64_t)ts.tv_nsec;
}

static void probe_crossing(void)
{
    struct timespec ts;
    syscall(SYS_clock_gettime, CLOCK_MONOTONIC, &ts);
    sink += (uint64_t)ts.tv_nsec;
}

static uint32_t xs32(uint32_t *s)
{
    uint32_t x = *s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return *s = x;
}

/* Розкладаємо сторінки буфера в перемішаний однозв'язний ланцюг: у першому
   слові кожної сторінки лежить зсув наступної. Перехід ланцюгом чіпає рівно
   одну лінію кешу на сторінку — тобто тисне на TLB, а не на кеш даних, —
   і порядок сторінок випадковий, тож наступний крок не вгадується наперед.
   Зсуви тримаємо в uint32_t: до 4 ГіБ вистачає із запасом. */
static void chain(uint8_t *buf, size_t pages)
{
    uint32_t *perm;
    uint32_t seed = 0x9e3779b9u;
    size_t i;

    if (!pages) return;                        /* інакше pages - 1 переповниться */
    perm = malloc(pages * sizeof *perm);
    if (!perm) { perror("malloc"); exit(1); }
    for (i = 0; i < pages; i++)
        perm[i] = (uint32_t)i;
    for (i = pages - 1; i > 0; i--) {          /* тасування Фішера — Єйтса */
        size_t j = xs32(&seed) % (i + 1);
        uint32_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    for (i = 0; i < pages; i++) {
        uint32_t here = perm[i] * PAGE;
        uint32_t next = perm[(i + 1) % pages] * PAGE;
        memcpy(buf + here, &next, sizeof next);
    }
    free(perm);
}

static uint64_t window(void (*fn)(void), size_t iters, uint8_t *buf, size_t pages)
{
    uint32_t off = 0;
    uint64_t t0, t1;
    size_t i;
    int s;

    /* Компілятор не має знати, яка саме функція в руках: інакше він
       підставить прямий виклик, а порожню пробу викине зовсім —
       і віднімати стане нічого. Рядок асемблера без жодної інструкції
       переконує його, що покажчик побував у невідомому коді. */
    __asm__ __volatile__("" : "+r"(fn));

    t0 = tsc_open();
    for (i = 0; i < iters; i++) {
        if (pages) {
            for (s = 0; s < STEPS; s++)
                memcpy(&off, buf + off, sizeof off);
            sink += off;
        }
        fn();
    }
    t1 = tsc_close();
    return t1 - t0;
}

/* Мінімум, а не середнє: усе, що трапляється в замірі, тільки додає такти.
   Тло віднімаємо таким самим мінімумом, знятим у тих самих умовах. */
static double cost(void (*fn)(void), size_t iters, uint8_t *buf,
                   size_t pages, int reps)
{
    uint64_t best = UINT64_MAX, base = UINT64_MAX;
    int r;

    window(fn, iters, buf, pages);              /* розігрів — викидаємо */
    window(probe_idle, iters, buf, pages);

    for (r = 0; r < reps; r++) {
        uint64_t a = window(fn, iters, buf, pages);
        uint64_t b = window(probe_idle, iters, buf, pages);
        if (a < best) best = a;
        if (b < base) base = b;
    }
    return ((double)best - (double)base) / (double)iters;
}

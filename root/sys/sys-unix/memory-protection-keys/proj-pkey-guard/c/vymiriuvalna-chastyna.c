struct region { char *base; size_t len; int key; };

typedef void (*runner)(struct region *, long);

static double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static void run_bare(struct region *r, long n)          /* підлога виміру */
{
    for (long i = 0; i < n; i++)
        *(volatile char *)r->base = (char)i;
}

static void run_pkey(struct region *r, long n)
{
    for (long i = 0; i < n; i++) {
        pkey_set(r->key, 0);
        *(volatile char *)r->base = (char)i;
        pkey_set(r->key, PKEY_DISABLE_WRITE);
    }
}

static void run_mprotect(struct region *r, long n)
{
    for (long i = 0; i < n; i++) {
        if (mprotect(r->base, r->len, PROT_READ | PROT_WRITE) < 0) goto bad;
        *(volatile char *)r->base = (char)i;
        if (mprotect(r->base, r->len, PROT_READ) < 0) goto bad;
    }
    return;
bad:
    perror("mprotect"); exit(1);
}

/* Ітерацій беремо не порівну, а стільки, щоб набрати спільний бюджет часу:
   ціни різняться на два-три порядки, і мільйон пар mprotect тривав би десятки секунд. */
static double bench(runner f, struct region *r, double budget_ns, long cap)
{
    long n = 64;
    f(r, 64);                                   /* прогрів */
    for (;;) {
        double t0 = now_ns();
        f(r, n);
        double dt = now_ns() - t0;
        if (dt >= budget_ns || n >= cap)
            return dt / (double)n;
        n = (n * 4 > cap) ? cap : n * 4;
    }
}

struct neighbour { pthread_t tid; char *a, *b; size_t len; int key, cpu; };

static _Atomic int stop_flag;

static void *neighbour_main(void *arg)
{
    struct neighbour *w = arg;
    cpu_set_t set;
    volatile char *a = (volatile char *)w->a;
    volatile char *b = (volatile char *)w->b;
    unsigned long acc = 0;

    /* PKRU успадковано в мить clone — але покладатися на це не можна:
       кожен потік ставить собі права сам і першою ж дією */
    pkey_set(w->key, PKEY_DISABLE_WRITE);

    CPU_ZERO(&set);
    CPU_SET(w->cpu, &set);
    pthread_setaffinity_np(pthread_self(), sizeof set, &set);

    while (!atomic_load_explicit(&stop_flag, memory_order_relaxed))
        for (size_t off = 0; off < w->len; off += (size_t)page_size)
            acc += (unsigned char)a[off] + (unsigned char)b[off];

    return (void *)acc;
}

static void bench_one(size_t npages, int nthreads)
{
    size_t len = npages * (size_t)page_size;
    struct region plain = { map_pages(npages), len, -1 };
    struct region keyed = { map_pages(npages), len, -1 };
    long ncpu = sysconf(_SC_NPROCESSORS_ONLN);
    struct neighbour *ws = NULL;
    double bare, mp, pk;
    int key = pkey_alloc(0, PKEY_DISABLE_WRITE);

    if (key < 0) { perror("pkey_alloc"); exit(1); }
    keyed.key = key;
    if (pkey_mprotect(keyed.base, len, PROT_READ | PROT_WRITE, key) < 0) {
        perror("pkey_mprotect"); exit(1);
    }

    atomic_store(&stop_flag, 0);
    if (nthreads > 0) {
        struct timespec settle = { 0, 50 * 1000 * 1000 };
        ws = calloc((size_t)nthreads, sizeof *ws);
        for (int i = 0; i < nthreads; i++) {
            ws[i].a = plain.base; ws[i].b = keyed.base;
            ws[i].len = len; ws[i].key = key;
            ws[i].cpu = (int)(1 + i % (ncpu > 1 ? ncpu - 1 : 1));
            if (pthread_create(&ws[i].tid, NULL, neighbour_main, &ws[i]) != 0) {
                perror("pthread_create"); exit(1);
            }
        }
        nanosleep(&settle, NULL);               /* дати їм осісти на своїх ядрах */
    }

    bare = bench(run_bare,     &plain, 1e8, 1L << 22);
    mp   = bench(run_mprotect, &plain, 3e8, 200000);
    mprotect(plain.base, len, PROT_READ | PROT_WRITE);
    pk   = bench(run_pkey,     &keyed, 3e8, 1000000);

    if (ws) {
        atomic_store(&stop_flag, 1);
        for (int i = 0; i < nthreads; i++) pthread_join(ws[i].tid, NULL);
        free(ws);
    }

    printf("%9zu %9d %13.0f %13.1f %10.0f× %12.1f\n",
           npages, nthreads, mp, pk, mp / pk, bare);

    pkey_mprotect(keyed.base, len, PROT_READ | PROT_WRITE, 0);
    pkey_free(key);
    munmap(plain.base, len);
    munmap(keyed.base, len);
}

int main(void)
{
    cpu_set_t set;

    page_size = sysconf(_SC_PAGESIZE);
    CPU_ZERO(&set); CPU_SET(0, &set);
    sched_setaffinity(0, sizeof set, &set);

    install_handler();
    demo_guard();

    printf("\n%9s %9s %13s %13s %11s %12s\n",
           "сторінок", "сусідів", "mprotect, нс", "pkey_set, нс", "разів", "підлога, нс");
    bench_one(1,    0);
    bench_one(1024, 0);
    bench_one(1,    8);
    bench_one(1024, 8);
    return 0;
}

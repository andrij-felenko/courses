static volatile uint64_t sink;

static void probe_idle() { }

static void probe_getppid()
{
    sink += static_cast<uint64_t>(syscall(SYS_getppid));
}

static void probe_vdso()
{
    struct timespec ts{};
    clock_gettime(CLOCK_MONOTONIC, &ts);
    sink += static_cast<uint64_t>(ts.tv_nsec);
}

static void probe_crossing()
{
    struct timespec ts{};
    syscall(SYS_clock_gettime, CLOCK_MONOTONIC, &ts);
    sink += static_cast<uint64_t>(ts.tv_nsec);
}

static uint32_t xs32(uint32_t& s)
{
    uint32_t x = s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return s = x;
}

/* Використовуємо std::vector для автоматичного керування пам'яттю
   та std::iota для заповнення початкової послідовності. */
static void chain(uint8_t* buf, std::size_t pages)
{
    if (!pages) return;
    std::vector<uint32_t> perm(pages);
    std::iota(perm.begin(), perm.end(), 0u);

    uint32_t seed = 0x9e3779b9u;
    for (std::size_t i = pages - 1; i > 0; --i) {
        std::size_t j = xs32(seed) % (i + 1);
        std::swap(perm[i], perm[j]);
    }
    for (std::size_t i = 0; i < pages; ++i) {
        uint32_t here = perm[i] * PAGE;
        uint32_t next = perm[(i + 1) % pages] * PAGE;
        std::memcpy(buf + here, &next, sizeof(next));
    }
}

static uint64_t window(void (*fn)(), std::size_t iters, uint8_t* buf, std::size_t pages)
{
    uint32_t off = 0;
    __asm__ __volatile__("" : "+r"(fn));

    uint64_t t0 = tsc_open();
    for (std::size_t i = 0; i < iters; ++i) {
        if (pages) {
            for (int s = 0; s < STEPS; ++s)
                std::memcpy(&off, buf + off, sizeof(off));
            sink += off;
        }
        fn();
    }
    uint64_t t1 = tsc_close();
    return t1 - t0;
}

static double cost(void (*fn)(), std::size_t iters, uint8_t* buf,
                    std::size_t pages, int reps)
{
    uint64_t best = UINT64_MAX, base = UINT64_MAX;

    window(fn, iters, buf, pages);
    window(probe_idle, iters, buf, pages);

    for (int r = 0; r < reps; ++r) {
        uint64_t a = window(fn, iters, buf, pages);
        uint64_t b = window(probe_idle, iters, buf, pages);
        if (a < best) best = a;
        if (b < base) base = b;
    }
    return (static_cast<double>(best) - static_cast<double>(base)) / static_cast<double>(iters);
}

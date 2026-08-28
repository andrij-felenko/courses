static uint64_t rng = 0x2545F4914F6CDD1DULL;

static inline uint64_t rnd64(void)          /* splitmix64 */
{
        uint64_t z = (rng += 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
}

/* Один цикл довжини n, побудований ПРЯМО В БУФЕРІ: масив, який
   перемішують, і є ланцюгом, тому зайвої пам'яті не треба. */
static void build_cycle(char *buf, size_t n)
{
        for (size_t k = 0; k < n; k++)              /* тотожність */
                *slot(buf, k) = k;

        for (size_t i = n - 1; i > 0; i--) {        /* Саттоло: 0 ≤ j < i */
                size_t j = (size_t)(rnd64() % (uint64_t)i);
                uintptr_t t = *slot(buf, i);
                *slot(buf, i) = *slot(buf, j);
                *slot(buf, j) = t;
        }

        for (size_t k = 0; k < n; k++) {            /* індекс → адреса */
                size_t nxt = (size_t)*slot(buf, k);
                *slot(buf, k) = (uintptr_t)(buf + node_off(nxt));
        }
}

static uint64_t splitmix64(uint64_t *s)
{
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* Кожна сторінка — власний детермінований шум від зерна (salt + номер сторінки).
   Однакове зерно для A і B робить їх побайтовими близнюками; далеке зерно для C
   робить кожну його сторінку унікальною. Нулями не заповнюємо: нульові сторінки
   ядро веде окремою дорогою (use_zero_pages), і дослід став би про інше. */
static void fill(unsigned char *base, uint64_t salt)
{
    unsigned long p, i;

    for (p = 0; p < NPAGES; p++) {
        uint64_t seed = salt + p;
        uint64_t *q = (uint64_t *)(base + p * PAGE);

        for (i = 0; i < PAGE / sizeof *q; i++)
            q[i] = splitmix64(&seed);
    }
}

static unsigned char *new_region(void)
{
    unsigned char *p = mmap(NULL, BYTES, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (p == MAP_FAILED) { perror("mmap"); exit(1); }

    if (madvise(p, BYTES, MADV_NOHUGEPAGE) != 0)
        fprintf(stderr, "MADV_NOHUGEPAGE: %s\n", strerror(errno));
    if (madvise(p, BYTES, MADV_MERGEABLE) != 0) {
        fprintf(stderr, "MADV_MERGEABLE: %s\n", strerror(errno));
        exit(1);
    }
    return p;                 /* успіх виклику ще НЕ означає, що злиття дозволено —
                                 перевіряємо це за прапорцем mg у smaps */
}

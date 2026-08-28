static volatile uint64_t sink;          /* щоб оптимізатор не викинув читання */

static void fill(volatile unsigned char *p, size_t n, uint64_t seq)
{
        for (size_t i = 0; i < n; i += CLINE)
                p[i] = (unsigned char)(seq + i);
        p[n - 1] = (unsigned char)seq;
}

static uint64_t sum(const volatile unsigned char *p, size_t n)
{
        uint64_t s = 0;
        for (size_t i = 0; i < n; i += CLINE)
                s += p[i];
        return s + p[n - 1];
}

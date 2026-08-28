static double now_sec(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

typedef float (*dot_fn)(const float *, const float *, size_t);

/* Час ОДНОГО проходу. volatile-приймач не дає компіляторові
   викинути виклик, у якого «результат нікому не потрібен».        */
static double bench(dot_fn f, const float *a, const float *b,
                    size_t n, int reps)
{
    static volatile float sink;
    f(a, b, n);                       /* прогрів: кеш і передбачувач */
    double t0 = now_sec();
    for (int r = 0; r < reps; r++)
        sink = f(a, b, n);
    return (now_sec() - t0) / reps;
}

static void report(const char *name, dot_fn f, const float *a,
                   const float *b, size_t n, int reps, double ref, double ghz)
{
    float got = f(a, b, n);
    double rel = fabs((double)got - ref) / fabs(ref);
    double dt  = bench(f, a, b, n, reps);
    printf("  %-22s  такти/елемент %6.2f   ГБ/с %7.1f   похибка %.1e\n",
           name, dt * ghz * 1e9 / n, 8.0 * n / dt / 1e9, rel);
}

int main(void)
{
    const double ghz = 3.0;                    /* підставте свою частоту */
    const size_t sizes[] = { 2048, 1u << 23 }; /* 8 КіБ і 32 МіБ на масив */
    const int    reps[]  = { 200000, 20 };

    for (int s = 0; s < 2; s++) {
        size_t n = sizes[s];
        /* aligned_alloc вимагає, щоб розмір був кратний вирівнюванню */
        float *a = aligned_alloc(64, n * sizeof *a);
        float *b = aligned_alloc(64, n * sizeof *b);
        for (size_t i = 0; i < n; i++) {
            a[i] = (float)rand() / RAND_MAX - 0.5f;
            b[i] = (float)rand() / RAND_MAX - 0.5f;
        }
        double ref = dot_ref(a, b, n);

        printf("\nn = %zu  (%.0f КіБ на масив)\n", n, n * sizeof *a / 1024.0);
        report("наївний цикл",     dot_naive, a, b, n, reps[s], ref, ghz);
        report("omp simd",         dot_omp,   a, b, n, reps[s], ref, ghz);
        report("AVX2, 8 акум.",    dot_avx2,  a, b, n, reps[s], ref, ghz);

        free(a); free(b);
    }
    return 0;
}

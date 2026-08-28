// відтворюваний ГПВЧ (LCG) — щоб не залежати від системного rand(); seed=0 теж коректний
static double rng_unit(uint64_t *st) {
    *st = *st * 6364136223846793005ULL + 1442695040888963407ULL;
    return (*st >> 11) * (1.0 / 9007199254740992.0);   // 53 біти → [0,1)
}

// трикутний розподіл: номінал — мода, кінці — межі
static double triangular(double lo, double nom, double hi, uint64_t *st) {
    double u = rng_unit(st);
    double c = (nom - lo) / (hi - lo);
    if (u < c) return lo + sqrt(u * (hi - lo) * (nom - lo));
    return hi - sqrt((1.0 - u) * (hi - lo) * (hi - nom));
}

static double draw(const Factor *f, uint64_t *st) {
    if (f->lo == f->hi) return f->nom;            // відоме точно → без розкиду
    return triangular(f->lo, f->nom, f->hi, st);
}

static int cmp_asc(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

// ── 3) Монте-Карло: тягнемо кожен множник багато разів і сортуємо ──
static void monte_carlo(double *out, int n, uint64_t seed) {
    uint64_t st = seed;                           // фіксований seed → відтворювано
    for (int k = 0; k < n; k++) {
        double v[NF];
        for (int i = 0; i < NF; i++) v[i] = draw(&FACTORS[i], &st);
        out[k] = peak_rps(v);
    }
    qsort(out, n, sizeof *out, cmp_asc);
}

static double pct(const double *s, int n, double p) {         // p-й перцентиль
    int i = (int)(p / 100.0 * n);
    return s[i < n ? i : n - 1];
}

static double frac_over(const double *s, int n, double thr) { // частка прогонів над порогом
    int lo = 0, hi = n;                           // перший індекс, де s[i] > thr
    while (lo < hi) { int m = (lo + hi) / 2; if (s[m] <= thr) lo = m + 1; else hi = m; }
    return 1.0 - (double)lo / n;
}

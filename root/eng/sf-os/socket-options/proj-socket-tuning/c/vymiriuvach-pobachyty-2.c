static const double EDGE[] = { 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 35, 45, 100 };
#define NB ((int)(sizeof EDGE / sizeof EDGE[0]) + 1)

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static void histogram(double *v, int n)
{
    int bin[NB];
    memset(bin, 0, sizeof bin);
    for (int i = 0; i < n; i++) {
        int b = NB - 1;
        for (int e = 0; e < NB - 1; e++)
            if (v[i] < EDGE[e]) { b = e; break; }
        bin[b]++;
    }

    int peak = 1;
    for (int b = 0; b < NB; b++) if (bin[b] > peak) peak = bin[b];

    for (int b = 0; b < NB; b++) {
        if (bin[b] == 0) continue;
        double lo = (b == 0) ? 0.0 : EDGE[b - 1];
        char hi[16];
        if (b == NB - 1) snprintf(hi, sizeof hi, "%6s", "inf");
        else             snprintf(hi, sizeof hi, "%6.2f", EDGE[b]);

        int w = bin[b] * 40 / peak;
        if (w == 0) w = 1;                    /* непорожній кошик має бути видно */
        printf("%6.2f - %s ms |", lo, hi);
        for (int k = 0; k < w; k++) putchar('#');
        printf(" %d\n", bin[b]);
    }

    qsort(v, (size_t)n, sizeof *v, cmp_double);
    int p99 = (int)(n * 0.99);
    if (p99 >= n) p99 = n - 1;
    printf("min %.2f  median %.2f  p99 %.2f  max %.2f ms\n",
           v[0], v[n / 2], v[p99], v[n - 1]);
}

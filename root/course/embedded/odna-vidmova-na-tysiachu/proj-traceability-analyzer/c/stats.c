#include "stats.h"

#include <math.h>
#include <stdlib.h>

double log_factorial(int n) {
    if (n <= 1) return 0.0;
    /* Прямий добуток переповнить double уже на 171!, тому працюємо в логарифмах. */
    return lgamma((double)n + 1.0);
}

double fisher_exact_2x2(Table2x2 t) {
    const int n1 = t.a + t.b, n0 = t.c + t.d;
    const int m1 = t.a + t.c, m0 = t.b + t.d;
    const int total = n1 + n0;
    if (total <= 0 || n1 == 0 || n0 == 0 || m1 == 0 || m0 == 0) return 1.0;

    /* Спільна частина гіпергеометричної ймовірності — рахуємо один раз. */
    const double log_denom = log_factorial(n1) + log_factorial(n0) +
                             log_factorial(m1) + log_factorial(m0) -
                             log_factorial(total);

    const double log_p_obs = log_denom - (log_factorial(t.a) + log_factorial(t.b) +
                                          log_factorial(t.c) + log_factorial(t.d));

    const int min_a = (m1 - n0 > 0) ? m1 - n0 : 0;
    const int max_a = (n1 < m1) ? n1 : m1;

    /* Двосторонній p — сума всіх розкладів, не ймовірніших за спостережений. */
    double p_total = 0.0;
    for (int x = min_a; x <= max_a; x++) {
        const int xb = n1 - x, xc = m1 - x, xd = n0 - xc;
        const double log_p = log_denom - (log_factorial(x) + log_factorial(xb) +
                                          log_factorial(xc) + log_factorial(xd));
        if (log_p <= log_p_obs + 1e-9) p_total += exp(log_p);
    }
    if (p_total > 1.0) p_total = 1.0;
    if (p_total < 0.0) p_total = 0.0;
    return p_total;
}

Effect effect_size(Table2x2 t) {
    Effect e = { 0.0, 0.0, 0.0, 0 };
    double a = t.a, b = t.b, c = t.c, d = t.d;

    /* Корекція Холдейна — Енскомба: без неї порожня клітинка дає OR = +inf. */
    if (a == 0.0 || b == 0.0 || c == 0.0 || d == 0.0) {
        a += 0.5; b += 0.5; c += 0.5; d += 0.5;
        e.haldane = 1;
    }
    e.odds_ratio = (a * d) / (b * c);

    const double se = sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
    const double ln_or = log(e.odds_ratio);
    e.ci_low  = exp(ln_or - 1.96 * se);
    e.ci_high = exp(ln_or + 1.96 * se);
    return e;
}

double chi2_tail_1df(double chi2) {
    if (!(chi2 > 0.0)) return 1.0;
    return erfc(sqrt(chi2 / 2.0));   /* хвіст χ² з одним ступенем свободи */
}

typedef struct { double p; size_t idx; } PIdx;

static int cmp_pidx(const void *x, const void *y) {
    const PIdx *a = x, *b = y;
    return (a->p > b->p) - (a->p < b->p);
}

int benjamini_hochberg(const double *p, size_t n, double *p_adj) {
    if (n == 0) return 0;
    PIdx *v = malloc(n * sizeof *v);
    if (!v) return -1;
    for (size_t i = 0; i < n; i++) { v[i].p = p[i]; v[i].idx = i; }
    qsort(v, n, sizeof *v, cmp_pidx);

    /* Ідемо від найбільшого p донизу, тримаючи монотонність. */
    double prev = 1.0;
    for (size_t k = n; k-- > 0;) {
        double q = v[k].p * (double)n / (double)(k + 1);
        if (q > prev) q = prev;
        if (q > 1.0)  q = 1.0;
        prev = q;
        p_adj[v[k].idx] = q;
    }
    free(v);
    return 0;
}

MhResult mantel_haenszel(const Table2x2 *strata, size_t n) {
    MhResult r = { 0.0, 0.0, 1.0, 0 };
    double num = 0.0, den = 0.0, sum_a = 0.0, sum_e = 0.0, sum_v = 0.0;

    for (size_t i = 0; i < n; i++) {
        const double a = strata[i].a, b = strata[i].b, c = strata[i].c, d = strata[i].d;
        const double N = a + b + c + d;
        if (N <= 1.0) continue;
        const double n1 = a + b, n0 = c + d, m1 = a + c, m0 = b + d;
        if (n1 == 0.0 || n0 == 0.0 || m1 == 0.0 || m0 == 0.0) continue;  /* страта без інформації */

        num += a * d / N;
        den += b * c / N;
        sum_a += a;
        sum_e += n1 * m1 / N;
        sum_v += n1 * n0 * m1 * m0 / (N * N * (N - 1.0));
        r.strata_used++;
    }
    if (r.strata_used == 0) { r.odds_ratio = NAN; r.p_value = NAN; return r; }

    r.odds_ratio = (den > 0.0) ? num / den : ((num > 0.0) ? INFINITY : NAN);

    if (sum_v > 0.0) {
        double dev = fabs(sum_a - sum_e) - 0.5;   /* поправка на неперервність */
        if (dev < 0.0) dev = 0.0;
        r.chi2 = dev * dev / sum_v;
        r.p_value = chi2_tail_1df(r.chi2);
    } else {
        r.chi2 = 0.0;
        r.p_value = 1.0;
    }
    return r;
}

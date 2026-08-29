#ifndef STATS_H
#define STATS_H

#include <stddef.h>

typedef struct { int a, b, c, d; } Table2x2;

typedef struct {
    double odds_ratio;
    double ci_low;
    double ci_high;
    int    haldane;      /* чи довелося додати 0.5 до кожної клітинки */
} Effect;

typedef struct {
    double odds_ratio;   /* INFINITY, коли в жодній страті немає b*c */
    double chi2;
    double p_value;
    size_t strata_used;
} MhResult;

double log_factorial(int n);
double fisher_exact_2x2(Table2x2 t);
Effect effect_size(Table2x2 t);
double chi2_tail_1df(double chi2);

/* Поправка Беньяміні — Хохберга; 0 або -1 при браку пам'яті. */
int benjamini_hochberg(const double *p, size_t n, double *p_adj);

/* Стратифікований аналіз Мантеля — Гензеля. */
MhResult mantel_haenszel(const Table2x2 *strata, size_t n);

#endif /* STATS_H */

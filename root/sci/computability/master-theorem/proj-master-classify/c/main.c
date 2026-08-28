#include <stdio.h>
#include <math.h>

/* Три випадки майстер-теореми — і чесна відмова, коли float не суддя. */
typedef enum { OUTSIDE = 0, LEAF = 1, BALANCE = 2, ROOT = 3 } Case;

typedef struct {
    Case        kind;   /* який випадок (або OUTSIDE — поза межами)  */
    double      cstar;  /* критичний показник  c* = log_b a          */
    const char *why;    /* чому OUTSIDE (для решти — порожньо)        */
} Verdict;

/* Баланс d == c* означає рівно b^d = a. Перевіряємо це в ЦІЛИХ —
   без ірраціонального логарифма: чи є ціле k ≈ d, для якого b^k == a. */
static int exact_balance(long a, long b, double d) {
    long k = lround(d);
    if (k < 0 || fabs(d - (double)k) > 1e-9) return 0;   /* d не ціле */
    long p = 1;
    for (long i = 0; i < k; i++) {
        if (p > a / b) return 0;        /* наступний множник перескочив би a */
        p *= b;
    }
    return p == a;
}

Verdict classify(long a, long b, double d) {
    Verdict v = { OUTSIDE, 0.0, "" };

    /* Пастка входу: a — кількість підзадач (>= 1); b — у скільки разів
       підзадача менша (>= 2, інакше вона не меншає й дна рекурсії нема). */
    if (a < 1 || b < 2) {
        v.why = "потрібні a >= 1 і b >= 2: підзадачі мусять меншати";
        return v;
    }

    double cstar = log((double)a) / log((double)b);      /* c* = log_b a */
    v.cstar = cstar;

    double gap = d - cstar;
    double eps = 1e-9 * (1.0 + fabs(cstar));             /* поріг числового шуму */

    if (gap < -eps) { v.kind = LEAF; return v; }         /* d < c*: панує листя  */
    if (gap >  eps) { v.kind = ROOT; return v; }         /* d > c*: панує корінь */

    /* |d - c*| у межах шуму — float мовчить. Підтверджуємо баланс точно. */
    if (exact_balance(a, b, d)) { v.kind = BALANCE; return v; }

    v.why = "d впритул до c*, та баланс не підтверджено точно "
            "(c* = log_b a, певно, ірраціональний) — тут треба точна арифметика";
    return v;
}

/* --- друк відповіді --- */
static void show_pow(char *buf, int n, double x) {
    if      (fabs(x)       < 1e-9) snprintf(buf, n, "1");   /* n^0 = 1 */
    else if (fabs(x - 1.0) < 1e-9) snprintf(buf, n, "n");   /* n^1 = n */
    else                           snprintf(buf, n, "n^%.6g", x);
}

static void report(const char *name, long a, long b, double d) {
    Verdict v = classify(a, b, d);
    char nc[32], nd[32];
    show_pow(nc, sizeof nc, v.cstar);
    show_pow(nd, sizeof nd, d);
    printf("%s (a=%ld, b=%ld, d=%g): ", name, a, b, d);
    switch (v.kind) {
        case LEAF:
            printf("випадок 1 — панує листя, T = Θ(%s)\n", nc);
            break;
        case BALANCE:
            if (fabs(v.cstar) < 1e-9)
                printf("випадок 2 — баланс, T = Θ(log n)\n");
            else
                printf("випадок 2 — баланс, T = Θ(%s · log n)\n", nc);
            break;
        case ROOT:
            printf("випадок 3 — панує корінь, T = Θ(%s)\n", nd);
            break;
        default:
            printf("поза межами — %s\n", v.why);
            break;
    }
}

int main(void) {
    report("сорт-злиттям",  2,    2, 1);   /* 2T(n/2)+n    -> баланс         */
    report("двійк-пошук",   1,    2, 0);   /*  T(n/2)+1    -> баланс (log n) */
    report("Карацуба",      3,    2, 1);   /* 3T(n/2)+n    -> листя n^1.585  */
    report("Штрассен",      7,    2, 2);   /* 7T(n/2)+n^2  -> листя n^2.807  */
    report("квадрат-поділ", 2,    2, 2);   /* 2T(n/2)+n^2  -> корінь n^2     */
    report("майже-тай",     2049, 2, 11);  /* c* ~ 11.0007 -> листя, не баланс */
    report("хибний-вхід",   3,    1, 1);   /* b=1: не меншає -> поза межами  */
    return 0;
}

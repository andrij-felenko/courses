#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t lo;
    int64_t hi;
} Interval;

Interval interval_add(Interval a, Interval b) {
    return (Interval){a.lo + b.lo, a.hi + b.hi};
}

Interval interval_sub(Interval a, Interval b) {
    return (Interval){a.lo - b.hi, a.hi - b.lo};
}

Interval interval_mul(Interval a, Interval b) {
    int64_t p1 = a.lo * b.lo, p2 = a.lo * b.hi;
    int64_t p3 = a.hi * b.lo, p4 = a.hi * b.hi;
    int64_t min_p = p1 < p2 ? p1 : p2;
    if (p3 < min_p) min_p = p3;
    if (p4 < min_p) min_p = p4;
    int64_t max_p = p1 > p2 ? p1 : p2;
    if (p3 > max_p) max_p = p3;
    if (p4 > max_p) max_p = p4;
    return (Interval){min_p, max_p};
}

Interval interval_sqr(Interval a) {
    if (a.lo <= 0 && a.hi >= 0) {
        int64_t m1 = a.lo * a.lo, m2 = a.hi * a.hi;
        return (Interval){0, m1 > m2 ? m1 : m2};
    }
    int64_t m1 = a.lo * a.lo, m2 = a.hi * a.hi;
    return (Interval){m1 < m2 ? m1 : m2, m1 > m2 ? m1 : m2};
}

bool interval_contains_zero(Interval a) {
    return a.lo <= 0 && a.hi >= 0;
}

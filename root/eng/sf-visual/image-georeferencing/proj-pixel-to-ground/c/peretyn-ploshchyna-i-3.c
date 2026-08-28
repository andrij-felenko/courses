static Status hit_terrain(const Shot *s, const double p0[3], const double d[3],
                          const Grid *g, double step, double eps, double *t_out)
{
    double g0;
    if (d[2] <= 0.0) return GEO_HORIZON;
    if (!gap(s, p0, d, g, 0.0, &g0) || g0 <= 0.0) return GEO_NO_HIT;

    double lo = 0.0;
    for (double t = step; t <= RANGE_MAX; t += step) {
        double gt;
        if (!gap(s, p0, d, g, t, &gt)) return GEO_NO_HIT;   /* промінь вийшов за сітку */
        if (gt <= 0.0) {
            double hi = t;                                   /* знак змінився: вилка [lo, hi] */
            while (hi - lo > eps) {
                double mid = 0.5*(lo + hi), gm;
                gap(s, p0, d, g, mid, &gm);
                if (gm > 0.0) lo = mid; else hi = mid;
            }
            *t_out = 0.5*(lo + hi);
            return GEO_OK;
        }
        lo = t;
    }
    return GEO_NO_HIT;
}

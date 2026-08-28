typedef struct { const char *name; double o_lo, o_hi, swing; } Bar;

static int cmp_swing_desc(const void *a, const void *b) {     // спад за розмахом
    double x = ((const Bar *)a)->swing, y = ((const Bar *)b)->swing;
    return (x < y) - (x > y);
}

// ── 4) торнадо: гойдаємо один множник, решту тримаємо на номіналі ──
static void tornado(Bar bars[NF]) {
    for (int i = 0; i < NF; i++) {
        double v[NF]; nominal(v);
        v[i] = FACTORS[i].lo; double o_lo = peak_rps(v);
        v[i] = FACTORS[i].hi; double o_hi = peak_rps(v);
        bars[i] = (Bar){ FACTORS[i].name, o_lo, o_hi, fabs(o_hi - o_lo) };
    }
    qsort(bars, NF, sizeof *bars, cmp_swing_desc);   // найдовший розмах згори
}

// заповнити вектор значень номіналами всіх множників
static void nominal(double v[NF]) {
    for (int i = 0; i < NF; i++) v[i] = FACTORS[i].nom;
}

// ── 1) точкова оцінка: усе на номіналі ──
static double point(void) {
    double v[NF]; nominal(v);
    return peak_rps(v);
}

// ── 2) інтервал: добуток додатних діапазонів монотонний → досить кінців ──
static void interval(double *lo, double *hi) {
    double vlo[NF], vhi[NF];
    for (int i = 0; i < NF; i++) { vlo[i] = FACTORS[i].lo; vhi[i] = FACTORS[i].hi; }
    *lo = peak_rps(vlo);   // усі нижні кінці
    *hi = peak_rps(vhi);   // усі верхні кінці
}

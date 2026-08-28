// Прогнати варіант у двох крайнощах: оптимістичній (усі p × 0.6)
// і песимістичній (усі p × 1.4, але не вище 1.0). Дає ВИЛКУ експозиції.
static void exposure_range(const Variant& v, double& lo, double& hi) {
    lo = hi = 0.0;
    for (int i = 0; i < v.count; ++i) {
        double p_lo = v.risks[i].p * 0.6;
        double p_hi = v.risks[i].p * 1.4;
        if (p_hi > 1.0) p_hi = 1.0;          // ймовірність не буває > 1
        lo += p_lo * v.risks[i].loss;
        hi += p_hi * v.risks[i].loss;
    }
}

// Чи стійкий вирок? Вирок надійний ЛИШЕ якщо вилки не перекриваються:
// найгірший випадок переможця все одно кращий за найкращий випадок суперника.
static void verdict_robust(const Variant& a, const Variant& b) {
    double a_lo, a_hi, b_lo, b_hi;
    exposure_range(a, a_lo, a_hi);
    exposure_range(b, b_lo, b_hi);
    printf("%s: %.1f .. %.1f\n", a.name, a_lo, a_hi);
    printf("%s: %.1f .. %.1f\n", b.name, b_lo, b_hi);
    if (a_hi < b_lo)
        printf("Вирок СТІЙКИЙ: %s кращий навіть у найгіршому для себе разі.\n", a.name);
    else if (b_hi < a_lo)
        printf("Вирок СТІЙКИЙ: %s кращий навіть у найгіршому для себе разі.\n", b.name);
    else
        printf("Вирок ХИТКИЙ: вилки перекриваються — цифри не вирішують, "
               "потрібні інші аргументи або точніші оцінки.\n");
}

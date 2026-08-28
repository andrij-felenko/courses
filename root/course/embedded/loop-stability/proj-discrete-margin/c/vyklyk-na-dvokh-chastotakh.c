static void analyze(const char *tag, const loop_t *L) {
    sweep_t s;
    run_sweep(L, 1.0, 200000.0, &s);      /* від 1 до 2·10⁵ рад/с — понад 5 декад */

    margins_t m = {0};
    find_phase_margin(&s, &m);
    find_gain_margin(&s, &m);
    double sm = vector_margin(L, &s);

    printf("=== %s (Ts = %.0f мкс) ===\n", tag, L->Ts * 1e6);
    if (m.has_gc)
        printf("  запас по фазі:       %6.1f°  на  %.0f рад/с\n", m.pm_deg, m.w_gc);
    else
        printf("  запас по фазі:       кросовера немає (петля ніде не доходить до 0 дБ)\n");
    if (m.has_pc)
        printf("  запас по підсиленню: %6.1f дБ на  %.0f рад/с\n", m.gm_db, m.w_pc);
    else
        printf("  запас по підсиленню: фаза не дістає −180° (нескінченний запас)\n");
    printf("  векторний запас Sₘ:  %6.2f\n\n", sm);
}

int main(void) {
    /* Спільний контур: механіка + давач + той самий ПІД. Міняємо лише Ts. */
    loop_t fast = {
        .wp_plant  = 40.0,      /* механічний полюс двигуна, рад/с          */
        .wp_sensor = 3000.0,    /* полюс давача-фільтра, рад/с              */
        .Kp = 16.0, .Ki = 60.0, .Kd = 0.006,
        .wd = 3500.0,           /* полюс фільтра похідної, рад/с            */
        .Ts = 125e-6,           /* 8 кГц                                   */
        .dc_gain = 3.5,
    };
    loop_t slow = fast;         /* усе те саме...                          */
    slow.Ts = 250e-6;           /* ...крім удвічі повільнішого циклу (4 кГц) */

    analyze("швидкий цикл", &fast);
    analyze("повільний цикл", &slow);
    return 0;
}

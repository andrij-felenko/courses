// Зібрати докупи: спроєктувати, перевірити ОП, оцінити розкид Q, попередити.
static void sk_design_checked(const sk_filter_type *ft, float fc, float R,
                              float gbw_hz, float cap_tol, sk_stage st[]) {
    uint8_t n = sk_design_filter(ft, fc, R, st);
    sk_report(ft, fc, st, n);
    float spread = sk_q_spread(cap_tol);
    for (uint8_t i = 0; i < n; i++) {
        if (!sk_opamp_ok(&st[i], gbw_hz, 100.0f))
            printf("  ! ланка %u: бракує смуги ОП (треба GBW >= %.0f кГц)\n",
                   i + 1, st[i].f0 * st[i].Q * 100.0f / 1000.0f);
        if (st[i].Q * spread > 3.0f)
            printf("  ! ланка %u: Q=%.2f при допуску гуляє до %.2f — бери точніші C\n",
                   i + 1, st[i].Q, st[i].Q * spread);
    }
}

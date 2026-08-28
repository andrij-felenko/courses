// Спроєктувати весь фільтр заданого типу під частоту зрізу fc і резистор R.
// out[] — масив під nstage ланок; повертає кількість заповнених ланок.
static uint8_t sk_design_filter(const sk_filter_type *ft,
                                float fc, float R, sk_stage out[]) {
    for (uint8_t i = 0; i < ft->nstage; i++) {
        out[i].R  = R;
        out[i].f0 = fc * ft->stage[i].fmul;   // частота ЦІЄЇ ланки
        out[i].Q  = ft->stage[i].Q;           // Q ЦІЄЇ ланки
        sk_design(&out[i]);                   // ідеал → E12 → фактичні
    }
    return ft->nstage;
}

// Друк підсумку (через UART/printf): що замовляли і що вийшло.
static void sk_report(const sk_filter_type *ft, float fc, sk_stage st[], uint8_t n) {
    printf("Фільтр: %s, зріз %.0f Гц\n", ft->name, fc);
    for (uint8_t i = 0; i < n; i++) {
        printf("  ланка %u: R=%.0f  C1=%.1f нФ  C2=%.1f нФ  ->  f0=%.0f Гц  Q=%.3f\n",
               i + 1, st[i].R,
               st[i].C1 * 1e9f, st[i].C2 * 1e9f,
               st[i].f0, st[i].Q);
    }
}

int test_design_meets_mask(void)
{
    FilterSpec spec = {
        .fp = 3400.0f, .fs = 4000.0f,
        .Ap_dB = 1.0f, .As_dB = 60.0f,
        .fs_sample = 16000.0f,
    };
    const float fc   = 0.5f * (spec.fp + spec.fs);
    const float beta = 0.1102f * (spec.As_dB - 8.7f);          // ≈ 5.65
    const float dw   = 2.0f*(float)M_PI*(spec.fs - spec.fp)/spec.fs_sample;
    int N = (int)ceilf((spec.As_dB - 8.0f) / (2.285f * dw)) + 1;
    if ((N & 1) == 0) N += 1;

    static float b[129];
    if (!firwin_lpf(b, N, fc, spec.fs_sample, WIN_KAISER, beta)) return 1;

    // Сітка ГУСТА біля країв і по всьому затриманню — інакше прогавимо викид (нижче).
    float freq[400];
    int ng = 0;
    for (float f = 50.0f; f < 0.5f*spec.fs_sample; f += 20.0f)   // рівномірно густо
        if (ng < 400) freq[ng++] = f;

    MaskResult r = fir_check_mask(b, N, &spec, freq, ng);
    if (!r.pass) {
        printf("ПРОВАЛ: виліз із маски на %.2f дБ при %.0f Гц (N=%d)\n",
               -r.worst_margin_dB, r.worst_freq, N);
        return 1;
    }
    if (r.worst_margin_dB < 1.0f)
        printf("УВАГА: запас лише %.2f дБ при %.0f Гц — фільтр на межі\n",
               r.worst_margin_dB, r.worst_freq);
    printf("OK: N=%d, крива в масці (запас %.2f дБ)\n", N, r.worst_margin_dB);
    return 0;
}

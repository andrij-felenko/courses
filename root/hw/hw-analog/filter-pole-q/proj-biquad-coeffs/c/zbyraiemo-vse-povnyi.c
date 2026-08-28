// ── Глобальний фільтр (живе між перериваннями) ───────────────────────────
static biquad         g_stage[2];      // дві ланки 4-го порядку
static biquad_cascade g_filter = { g_stage, 2 };

// Налаштувати фільтр один раз при старті (чи при зміні режиму).
void filter_setup(float fc, float fs)
{
    build_lowpass(g_stage, BUTTERWORTH_4, 2, fc, fs);
    cascade_reset(&g_filter);

    // перевірка коефіцієнтів: підсилення на нулі має бути ≈ 1 для ФНЧ
    float dc = cascade_dc_gain(&g_filter);
    (void)dc;                           // assert(fabsf(dc - 1.0f) < 0.01f);
}

// Викликається на КОЖЕН семпл з АЦП (у перериванні чи в циклі обробки).
float filter_sample(float adc_value)
{
    return cascade_process(&g_filter, adc_value);
}

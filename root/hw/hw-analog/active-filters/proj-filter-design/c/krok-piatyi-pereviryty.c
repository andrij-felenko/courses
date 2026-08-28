// Магнітуда однієї ланки ФНЧ на частоті f (в разах, не дБ).
static float sk_mag_stage(const sk_stage *s, float f) {
    float r  = f / s->f0;
    float re = 1.0f - r * r;             // (1 − r²)
    float im = r / s->Q;                 // (r/Q)
    return 1.0f / sqrtf(re * re + im * im);
}

// Магнітуда всього каскаду на частоті f, у децибелах.
static float sk_mag_db(const sk_stage st[], uint8_t n, float f) {
    float mag = 1.0f;
    for (uint8_t i = 0; i < n; i++)
        mag *= sk_mag_stage(&st[i], f);  // добуток ланок
    return 20.0f * log10f(mag);          // у дБ
}

// Прогнати характеристику по частотах (лог-крок) і надрукувати — для звірки форми.
static void sk_sweep(const sk_stage st[], uint8_t n,
                     float f_min, float f_max, int per_decade) {
    float mult = powf(10.0f, 1.0f / per_decade);
    for (float f = f_min; f <= f_max * 1.001f; f *= mult)
        printf("%8.0f Гц   %+7.2f дБ\n", f, sk_mag_db(st, n, f));
}

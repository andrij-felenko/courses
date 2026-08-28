// Потоковий цикл: щотакту одні свіжі цифри входять, один готовий код виходить.
// samples[] — вхідні відліки; на кожен ми моделюємо аналогову частину (stage_15bit),
// а бек-енд вирівнює й складає. У реальному приладі raw[] і final2 приходять із заліза.
void run_stream(const int32_t *samples, int n, uint16_t *codes_out) {
    backend_t be;
    be_init(&be);
    int out = 0;

    for (int i = 0; i < n; ++i) {
        // ── аналогова частина: прогнати відлік крізь щаблі, зібрати сирі цифри ──
        uint8_t raw[NSTAGE];
        int32_t v = samples[i];
        for (int s = 0; s < NSTAGE; ++s) {
            int32_t vres;
            raw[s] = stage_15bit(v, /*offset=*/0, &vres);   // у житті — з заліза
            v = vres;
        }
        // хвіст-flash: залишок останнього щабля → 2 біти
        int32_t VREF = 1 << 15;
        int q = (int)(((int64_t)(v + VREF) * 4) / (2 * VREF));
        uint8_t final2 = (uint8_t)(q < 0 ? 0 : q > 3 ? 3 : q);

        // ── цифровий бек-енд: вирівняти в часі й скласти ──
        uint16_t code;
        if (be_step(&be, raw, final2, &code))
            codes_out[out++] = code;     // код відліку, що зайшов LAT тактів тому
    }
}

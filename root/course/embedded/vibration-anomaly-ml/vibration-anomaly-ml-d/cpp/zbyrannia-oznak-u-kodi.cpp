// window[] — заздалегідь пораховане вікно Ганна у Flash (прибирає витік спектра).
// re[], im[] — робочі буфери FFT. bandpass_env[] — буфер обвідної.
static void make_features(const int16_t *s, float *feat)
{
    // ── (1) Звичайний спектр: ловить дисбаланс, розцентровку ─────────
    float re[N], im[N];
    for (int i = 0; i < N; i++) { re[i] = s[i] * window[i]; im[i] = 0.0f; }
    fft_radix2(re, im, N);                      // FFT на місці

    int fi = 0;
    const int per_band = (N / 2) / 12;          // 12 смуг звичайного спектра
    for (int b = 0; b < 12; b++) {
        float e = 1e-6f;
        for (int k = 0; k < per_band; k++) {
            int idx = b * per_band + k;
            e += re[idx]*re[idx] + im[idx]*im[idx];
        }
        feat[fi++] = logf(e);                   // лог зрівнює малі й великі смуги
    }

    // ── (2) Демодуляція обвідної: ловить ПІДШИПНИК ──────────────────
    // Смуговий фільтр біля резонансу корпусу (тут ~4 кГц) + випрямлення.
    for (int i = 0; i < N; i++)
        bandpass_env[i] = fabsf(bandpass(s[i]));   // |смуговий фільтр(сигнал)|
    // Тепер спектр ОБВІДНОЇ: у ньому BPFO стоїть чистим піком.
    for (int i = 0; i < N; i++) { re[i] = bandpass_env[i]*window[i]; im[i] = 0.0f; }
    fft_radix2(re, im, N);
    const int env_band = (N / 2) / 8;           // 8 смуг спектра обвідної
    for (int b = 0; b < 8; b++) {
        float e = 1e-6f;
        for (int k = 0; k < env_band; k++) {
            int idx = b * env_band + k;
            e += re[idx]*re[idx] + im[idx]*im[idx];
        }
        feat[fi++] = logf(e);
    }

    // ── (3) Моменти у часі: ранні ознаки ударності ──────────────────
    float mean = 0.0f;
    for (int i = 0; i < N; i++) mean += s[i];
    mean /= N;
    float m2 = 0.0f, m4 = 0.0f, peak = 0.0f;
    for (int i = 0; i < N; i++) {
        float d = s[i] - mean;
        float d2 = d * d;
        m2 += d2;                                // Σ(x−μ)²  → дисперсія
        m4 += d2 * d2;                           // Σ(x−μ)⁴  → для куртозису
        if (fabsf(d) > peak) peak = fabsf(d);
    }
    m2 /= N; m4 /= N;
    float rms  = sqrtf(m2);
    float kurt = m4 / (m2 * m2);                 // = Σ(x−μ)⁴/N ÷ σ⁴  (здоровий ≈ 3)
    float crest = peak / (rms + 1e-6f);

    feat[fi++] = logf(rms + 1e-6f);
    feat[fi++] = kurt;                           // без лога: сам по собі в діапазоні ~3..40
    feat[fi++] = crest;
    // fi == N_FEAT: 12 смуг спектра + 8 смуг обвідної + 3 моменти = 23 — вектор зібрано.
}

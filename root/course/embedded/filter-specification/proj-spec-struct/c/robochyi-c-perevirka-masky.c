// Результат перевірки: вкладається чи ні, і ДЕ найгірше порушення.
// worst_margin_dB — запас до маски: додатний = є запас, від'ємний = вилізли
// (і на скільки дБ); найкорисніше число, бо каже не лише "ні", а "наскільки".
typedef struct {
    bool  pass;
    float worst_margin_dB;   // мінімальний запас по всій кривій, дБ
    float worst_freq;        // частота, де цей найгірший запас
} SpecResult;

// Перевірити характеристику (mag[i] на частоті freq[i], n точок) проти маски.
SpecResult spec_check(const FilterSpec *s,
                      const float *freq, const float *mag, size_t n)
{
    SpecResult r = { .pass = true, .worst_margin_dB = 1e9f, .worst_freq = 0.0f };

    // Межі коридору, переведені в дБ ОДИН раз (не в циклі):
    //  у пропусканні крива мусить бути НЕ НИЖЧЕ −Ap_dB;
    //  у затриманні  —              НЕ ВИЩЕ  −As_dB.
    const float passband_floor_dB = -s->Ap_dB;   // напр. −1 дБ
    const float stopband_ceil_dB  = -s->As_dB;   // напр. −60 дБ
    const float nyquist = 0.5f * s->fs_sample;   // стеля частот

    for (size_t i = 0; i < n; ++i) {
        float f  = freq[i];
        float db = lin_to_db(mag[i]);            // крива в дБ

        // Частоти вище Найквіста для цифрового фільтра не існують — пропуск.
        if (f > nyquist) continue;

        if (f <= s->fp) {
            // ── СМУГА ПРОПУСКАННЯ: не нижче підлоги брижів ──────────────
            float margin = db - passband_floor_dB;   // >0 якщо вище підлоги
            if (margin < r.worst_margin_dB) {
                r.worst_margin_dB = margin;
                r.worst_freq = f;
            }
            if (db < passband_floor_dB) r.pass = false;   // впала нижче — провал

        } else if (f >= s->fs) {
            // ── СМУГА ЗАТРИМАННЯ: не вище стелі придушення ─────────────
            float margin = stopband_ceil_dB - db;    // >0 якщо нижче стелі
            if (margin < r.worst_margin_dB) {
                r.worst_margin_dB = margin;
                r.worst_freq = f;
            }
            if (db > stopband_ceil_dB) r.pass = false;    // піднялась — провал

        } else {
            // ── ПЕРЕХІДНА СМУГА (fp < f < fs): не нормована — пропуск ──
            continue;
        }
    }
    return r;
}

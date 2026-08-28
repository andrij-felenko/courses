typedef struct {
    float fp, fs;          // краї смуг, Гц
    float Ap_dB, As_dB;    // дозволені брижі / потрібне придушення, дБ (додатні)
    float fs_sample;       // частота дискретизації, Гц
} FilterSpec;

typedef struct {
    bool  pass;
    float worst_margin_dB; // мінімальний запас до маски (>0 запас, <0 виліз)
    float worst_freq;      // частота найгіршого запасу
} MaskResult;

// дБ амплітуди ↔ рази, із захистом log10(0)
static float lin_to_db(float mag) {
    float m = fabsf(mag);
    if (m < 1e-12f) m = 1e-12f;          // −240 дБ ≈ «практично нуль»
    return 20.0f * log10f(m);
}

// Перевірити коефіцієнти b[0..N-1] проти маски на сітці freq[0..ng-1].
MaskResult fir_check_mask(const float *b, int N, const FilterSpec *s,
                          const float *freq, int ng)
{
    MaskResult r = { .pass = true, .worst_margin_dB = 1e9f, .worst_freq = 0.0f };

    const float pass_floor_dB = -s->Ap_dB;   // підлога пропускання, напр. −1 дБ
    const float stop_ceil_dB  = -s->As_dB;   // стеля затримання,   напр. −60 дБ
    const float nyquist       = 0.5f * s->fs_sample;

    for (int i = 0; i < ng; ++i) {
        float f = freq[i];
        if (f > nyquist) continue;            // вище Найквіста частот нема

        float db = lin_to_db(fir_mag_at(b, N, f, s->fs_sample));

        if (f <= s->fp) {                     // ── ПРОПУСКАННЯ: не нижче підлоги
            float margin = db - pass_floor_dB;
            if (margin < r.worst_margin_dB) { r.worst_margin_dB = margin; r.worst_freq = f; }
            if (db < pass_floor_dB) r.pass = false;

        } else if (f >= s->fs) {              // ── ЗАТРИМАННЯ: не вище стелі
            float margin = stop_ceil_dB - db;
            if (margin < r.worst_margin_dB) { r.worst_margin_dB = margin; r.worst_freq = f; }
            if (db > stop_ceil_dB) r.pass = false;
        }
        // інакше — перехідна смуга (fp < f < fs): не нормована, пропуск
    }
    return r;
}

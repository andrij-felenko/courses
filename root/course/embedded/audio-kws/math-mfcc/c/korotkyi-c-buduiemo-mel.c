#include <math.h>
#include <stdint.h>

#define N_MEL   40          // скільки мел-смуг на виході
#define N_FFT   512         // довжина ШПФ
#define N_BIN   (N_FFT/2+1)  // корисних бінів спектра потужності: 257

// герци → мели й назад (найуживаніша форма з константами 2595 і 700)
static inline float hz_to_mel(float f) { return 2595.0f * log10f(1.0f + f / 700.0f); }
static inline float mel_to_hz(float m) { return 700.0f * (powf(10.0f, m / 2595.0f) - 1.0f); }

// фільтрбанк у розрідженій формі: для кожної смуги — [lo..hi) бінів і їхні ваги
typedef struct {
    int   lo[N_MEL];              // перший бін смуги (включно)
    int   hi[N_MEL];              // за-останній бін смуги (виключно)
    float w[N_MEL][N_BIN];        // трикутні ваги (ненульові лише в [lo..hi))
} MelBank;

// будуємо ОДИН раз при старті
void mel_bank_build(MelBank *b, float sr, float f_low, float f_high) {
    // 1. n_mel+2 рівновіддалені у МЕЛАХ точки → назад у герци → у номери бінів
    float m_low = hz_to_mel(f_low), m_high = hz_to_mel(f_high);
    int   edge[N_MEL + 2];
    for (int i = 0; i < N_MEL + 2; i++) {
        float m  = m_low + (m_high - m_low) * (float)i / (N_MEL + 1); // рівний крок у мелах
        float hz = mel_to_hz(m);
        int   k  = (int)lroundf(hz * N_FFT / sr);                     // → бін ШПФ
        edge[i]  = k < 0 ? 0 : (k > N_BIN - 1 ? N_BIN - 1 : k);       // затиск у межі
    }
    // 2. трикутник i: лівий край edge[i], вершина edge[i+1], правий edge[i+2]
    for (int i = 0; i < N_MEL; i++) {
        int lo = edge[i], ce = edge[i + 1], hi = edge[i + 2];
        b->lo[i] = lo;
        b->hi[i] = hi;
        for (int k = 0; k < N_BIN; k++) b->w[i][k] = 0.0f;
        for (int k = lo; k < ce; k++)                 // лівий схил: 0 → 1
            b->w[i][k] = (ce > lo) ? (float)(k - lo) / (ce - lo) : 0.0f;
        for (int k = ce; k < hi; k++)                 // правий схил: 1 → 0
            b->w[i][k] = (hi > ce) ? (float)(hi - k) / (hi - ce) : 0.0f;
    }
}

// щокадру: спектр потужності power[N_BIN] → лог-мел-смуги logmel[N_MEL]
void mel_apply(const MelBank *b, const float power[N_BIN], float logmel[N_MEL]) {
    for (int i = 0; i < N_MEL; i++) {
        float s = 0.0f;
        for (int k = b->lo[i]; k < b->hi[i]; k++)     // лише накриті біни — дешево
            s += b->w[i][k] * power[k];
        logmel[i] = logf(s + 1e-6f);                  // ε проти log(0); ← готова ознака для CNN
    }
}

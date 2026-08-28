#include <math.h>

// Стеля SNR, яку ставить тремтіння такту (джиттер).
// f  — частота вхідного сигналу, Гц;  tj — RMS-джиттер, с.
float jitter_snr_db(float f, float tj) {
    return -20.0f * log10f(2.0f * 3.14159265f * f * tj);
}

float f  = 10.0e6f;     // 10 МГц вхід
float tj = 1.0e-12f;    // 1 пс RMS джиттер такту

float snr = jitter_snr_db(f, tj);
// 2π·f·tj = 6.2832 · 1e7 · 1e-12 = 6.283e-5
// SNR = -20·log10(6.283e-5) ≈ 84.0 дБ

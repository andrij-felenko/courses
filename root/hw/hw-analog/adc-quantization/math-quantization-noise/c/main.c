#include <stdio.h>
#include <math.h>

int main(void) {
    const int   N    = 12;        // розрядність
    const float Vfs  = 3.3f;      // повна шкала, В
    const float levels = (float)(1u << N);   // 2^N = 4096 рівнів

    // 1) крок квантування
    float q = Vfs / levels;                          // 3.3/4096 ≈ 0.806 мВ

    // 2) RMS шуму квантування з рівномірного розподілу: q/√12
    float e_rms = q / sqrtf(12.0f);                  // ≈ 0.233 мВ

    // 3) RMS повношкального синуса: амплітуда/√2, амплітуда = Vfs/2
    float sig_rms = (Vfs / 2.0f) / sqrtf(2.0f);      // ≈ 1.167 В

    // 4) SNR як відношення RMS у децибелах (за напругою → 20·log10)
    float snr_built = 20.0f * log10f(sig_rms / e_rms);

    // 5) та сама величина з готової формули
    float snr_formula = 6.02f * N + 1.76f;

    printf("крок q          = %.4f мВ\n", q * 1e3f);
    printf("шум  e_rms      = %.4f мВ  (= q/sqrt(12))\n", e_rms * 1e3f);
    printf("сигнал sig_rms  = %.4f В   (= (Vfs/2)/sqrt(2))\n", sig_rms);
    printf("SNR зібраний    = %.2f дБ\n", snr_built);
    printf("SNR за формулою = %.2f дБ\n", snr_formula);
    return 0;
}

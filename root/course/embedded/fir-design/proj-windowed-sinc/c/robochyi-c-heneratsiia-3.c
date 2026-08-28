#define FS_SAMPLE   16000.0f
#define FP          3400.0f      // край пропускання (мова)
#define FS_STOP     4000.0f      // край затримання
#define AS_DB       60.0f        // потрібне придушення

void design_demo(void)
{
    const float fc = 0.5f * (FP + FS_STOP);          // центр переходу = 3700 Гц

    // β під As за формулою Кайзера (третя гілка, бо As > 50 дБ) — як у статті
    const float beta = 0.1102f * (AS_DB - 8.7f);     // ≈ 5.65

    // Оцінка довжини за Кайзером (точніша за прикидку Гарріса):
    //   N ≈ (As − 8) / (2.285 · Δω) + 1,   Δω — ширина переходу в радіанах
    const float dw = 2.0f * (float)M_PI * (FS_STOP - FP) / FS_SAMPLE;  // ≈ 0.2356
    int N = (int)ceilf((AS_DB - 8.0f) / (2.285f * dw)) + 1;           // ≈ 98
    if ((N & 1) == 0) N += 1;                          // зробимо непарним → точний центр

    static float b[129];                              // з запасом під N
    if (firwin_lpf(b, N, fc, FS_SAMPLE, WIN_KAISER, beta)) {
        // b[] готовий: нормований по DC, лінійно-фазовий КІХ-ФНЧ
    }
}

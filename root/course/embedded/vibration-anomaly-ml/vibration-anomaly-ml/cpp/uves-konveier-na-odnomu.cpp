#define N        256          // розмір вікна FFT (степінь двійки)
#define N_BANDS  16           // скільки частотних смуг у векторі ознак

// window[] — заздалегідь пораховане вікно Ганна, вшите у Flash як константа.
// re[], im[] — робочі буфери для FFT (im занулюємо, вхід дійсний).
static void make_features(const int16_t *samples, float *feat)
{
    float re[N], im[N];

    // 1. Вікно: прибираємо краї шматка, щоб піки в спектрі не розмазувались.
    for (int i = 0; i < N; i++) {
        re[i] = (float)samples[i] * window[i];
        im[i] = 0.0f;
    }

    fft_radix2(re, im, N);     // 2. FFT на місці: re/im стають спектром

    // 3. Енергію дзеркальних бінів (0..N/2) розкладаємо по N_BANDS смугах.
    const int per_band = (N / 2) / N_BANDS;
    for (int b = 0; b < N_BANDS; b++) {
        float energy = 0.0f;
        for (int k = 0; k < per_band; k++) {
            int idx = b * per_band + k;
            energy += re[idx]*re[idx] + im[idx]*im[idx];   // |спектр|²
        }
        feat[b] = logf(energy + 1e-6f);   // лог робить малі й великі смуги сумірними
    }
}

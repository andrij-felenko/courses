// Готову обвідну (env_buf) перетворюємо у спектр і шукаємо пік BPFO.
#include <math.h>

void analyze_envelope(float *env_buf, float fr, float bpfo_mult) {
    // 0) прибрати постійну складову (та сама 2/π від випрямлення)
    float mean = 0.0f;
    for (int i = 0; i < ENV_N; i++) mean += env_buf[i];
    mean /= ENV_N;
    for (int i = 0; i < ENV_N; i++) env_buf[i] -= mean;

    // 1) вікно Ганна — щоб пік BPFO не «розмазався»
    for (int i = 0; i < ENV_N; i++) {
        float w = 0.5f * (1.0f - cosf(2.0f * 3.14159265f * i / (ENV_N - 1)));
        env_buf[i] *= w;
    }

    // 2) ШПФ (будь-яка бібліотека); результат — магнітуди mag[0..ENV_N/2]
    float mag[ENV_N / 2 + 1];
    fft_magnitude(env_buf, mag, ENV_N);       // ваша реалізація/бібліотека

    // 3) адреса BPFO на ЗНИЖЕНІЙ частоті
    const float fs_dec = FS_RAW / DECIM;      // = 2000 Гц
    float f_bpfo = bpfo_mult * fr;            // напр. 3.6 × оберти
    int   k      = (int)(f_bpfo * ENV_N / fs_dec + 0.5f);

    // 4) висота піка — беремо максимум у вузькому вікні ±2 біни
    //    (BPFO трохи «плаває» через прослизання кульок — рідко рівно цілий бін)
    float peak = 0.0f;
    for (int j = k - 2; j <= k + 2; j++)
        if (j > 0 && j <= ENV_N / 2 && mag[j] > peak) peak = mag[j];

    report_bpfo_level(peak);                   // далі — порівняння з еталоном
}

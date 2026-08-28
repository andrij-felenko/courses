#include <math.h>

// Налаштувати біквад на СМУГОВИЙ фільтр із центром f0 і добротністю Q.
void biquad_bandpass(biquad_t *f, float f0, float fs, float Q) {
    float w0    = 2.0f * 3.14159265f * f0 / fs;   // нормована частота, рад/відлік
    float cosw0 = cosf(w0);
    float alpha = sinf(w0) / (2.0f * Q);          // визначає ширину смуги

    // band-pass із сталим піковим підсиленням (constant 0 dB peak)
    float b0 =   alpha;
    float b1 =   0.0f;
    float b2 =  -alpha;
    float a0 =   1.0f + alpha;
    float a1 =  -2.0f * cosw0;
    float a2 =   1.0f - alpha;

    // нормуємо на a0 — щоб у step не ділити щоразу
    f->b0 = b0 / a0;  f->b1 = b1 / a0;  f->b2 = b2 / a0;
    f->a1 = a1 / a0;  f->a2 = a2 / a0;
    f->z1 = f->z2 = 0.0f;
}

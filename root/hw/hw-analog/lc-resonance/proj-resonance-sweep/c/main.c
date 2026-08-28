#include <stdint.h>

// --- Апаратна абстракція (реалізується під конкретну плату) ---
void     gen_set_freq(float hz);   // виставити частоту генератора
void     delay_ms(uint32_t ms);    // пауза, мілісекунди
uint16_t adc_read(void);           // один відлік детектора амплітуди

// Усереднити кілька відліків детектора — дешева страховка від шуму.
static float measure_amplitude(uint8_t averages) {
    uint32_t acc = 0;
    for (uint8_t i = 0; i < averages; ++i)
        acc += adc_read();
    return (float)acc / averages;
}

// Один прохід свіпу: заповнити freq[]/amp[], повернути кількість точок.
static int sweep(float f_min, float f_max, float f_step, float q_guess,
                 float *freq, float *amp, int max_pts) {
    int steps = (int)((f_max - f_min) / f_step) + 1;
    if (steps > max_pts) steps = max_pts;

    for (int i = 0; i < steps; ++i) {
        float f = f_min + i * f_step;
        gen_set_freq(f);

        // Контур розгойдується ~Q періодів — чекаємо кілька Q/f із запасом.
        uint32_t settle_ms = (uint32_t)(3.0f * q_guess / f * 1000.0f + 0.5f);
        delay_ms(settle_ms);

        freq[i] = f;
        amp[i]  = measure_amplitude(8);   // 8 відліків на точку
    }
    return steps;
}

// За готовими масивами: пік дає f0, смуга на рівні 0.707·max дає Q.
static void find_resonance(const float *freq, const float *amp, int n,
                           float *f0, float *q) {
    int peak = 0;
    for (int i = 1; i < n; ++i)
        if (amp[i] > amp[peak]) peak = i;
    *f0 = freq[peak];

    float half = 0.70710678f * amp[peak];   // 1/√2 від максимуму

    // Ліва межа смуги: від піка вліво до падіння нижче half,
    // уточнити частоту лінійною інтерполяцією між сусідніми точками.
    float f_lo = freq[0];
    for (int i = peak; i > 0; --i)
        if (amp[i - 1] < half) {
            float t = (half - amp[i - 1]) / (amp[i] - amp[i - 1]);
            f_lo = freq[i - 1] + t * (freq[i] - freq[i - 1]);
            break;
        }

    // Права межа — симетрично, від піка вправо.
    float f_hi = freq[n - 1];
    for (int i = peak; i < n - 1; ++i)
        if (amp[i + 1] < half) {
            float t = (half - amp[i + 1]) / (amp[i] - amp[i + 1]);
            f_hi = freq[i + 1] + t * (freq[i] - freq[i + 1]);
            break;
        }

    *q = *f0 / (f_hi - f_lo);   // Q = f0 / Δf
}

// Повний вимір: грубий прохід по діапазону, тоді тонкий навколо горба.
void find_lc_resonance(float f_min, float f_max, float q_guess,
                       float *f0, float *q) {
    float freq[64], amp[64];

    // Грубо: рідка сітка на весь діапазон (~30 точок).
    float coarse_step = (f_max - f_min) / 30.0f;
    int n = sweep(f_min, f_max, coarse_step, q_guess, freq, amp, 64);
    find_resonance(freq, amp, n, f0, q);

    // Тонко: вузьке вікно ±2·Δf навколо f0, крок ≤ Δf/5.
    float bw = *f0 / *q;
    n = sweep(*f0 - 2.0f * bw, *f0 + 2.0f * bw, bw / 5.0f, q_guess,
              freq, amp, 64);
    find_resonance(freq, amp, n, f0, q);
}

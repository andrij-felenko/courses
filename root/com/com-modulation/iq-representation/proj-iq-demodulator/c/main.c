#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура для збереження квадратурного відліку в декартових координатах
typedef struct {
    float i;
    float q;
} iq_sample_t;

// Перетворення полярних координат (амплітуда A, фаза phi) у прямокутні (I, Q)
static inline iq_sample_t polar_to_iq(float amp, float phase_rad) {
    iq_sample_t s;
    s.i = amp * cosf(phase_rad);
    s.q = amp * sinf(phase_rad);
    return s;
}

// Перетворення прямокутних компонент (I, Q) у полярні координати (амплітуда A, фаза phi)
static inline void iq_to_polar(iq_sample_t s, float *amp, float *phase_rad) {
    *amp = sqrtf(s.i * s.i + s.q * s.q);
    *phase_rad = atan2f(s.q, s.i);
}

// Рекурсивний ФНЧ першого порядку (Exponential Moving Average Filter)
typedef struct {
    float alpha;
    float state;
} lpf_1pole_t;

static inline float lpf_process(lpf_1pole_t *f, float in) {
    f->state += f->alpha * (in - f->state);
    return f->state;
}

// Функція корекції постійної складової (DC offset removal)
void correct_dc_offset(iq_sample_t *samples, size_t count) {
    if (!samples || count == 0) return;

    float sum_i = 0.0f;
    float sum_q = 0.0f;

    for (size_t n = 0; n < count; ++n) {
        sum_i += samples[n].i;
        sum_q += samples[n].q;
    }

    float mean_i = sum_i / (float)count;
    float mean_q = sum_q / (float)count;

    for (size_t n = 0; n < count; ++n) {
        samples[n].i -= mean_i;
        samples[n].q -= mean_q;
    }
}

// Повний конвеєр модуляції, цифрового переносу та демодуляції
void run_iq_pipeline(size_t num_samples, float sample_rate, float carrier_freq) {
    iq_sample_t *tx_iq = (iq_sample_t *)malloc(num_samples * sizeof(iq_sample_t));
    float *rf_signal = (float *)malloc(num_samples * sizeof(float));
    iq_sample_t *rx_iq = (iq_sample_t *)malloc(num_samples * sizeof(iq_sample_t));

    if (!tx_iq || !rf_signal || !rx_iq) {
        free(tx_iq); free(rf_signal); free(rx_iq);
        return;
    }

    // 1. Генерація базового IQ-сигналу (вектор, що обертається з частотою 1 кГц)
    float mod_freq = 1000.0f;
    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float phase = 2.0f * (float)M_PI * mod_freq * t;
        tx_iq[n] = polar_to_iq(1.0f, phase);
    }

    // 2. Цифровий квадратурний модулятор (Upconversion)
    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float wc = 2.0f * (float)M_PI * carrier_freq * t;
        rf_signal[n] = tx_iq[n].i * cosf(wc) - tx_iq[n].q * sinf(wc);
    }

    // 3. Цифровий квадратурний демодулятор (Downconversion + ФНЧ)
    lpf_1pole_t lpf_i = { .alpha = 0.05f, .state = 0.0f };
    lpf_1pole_t lpf_q = { .alpha = 0.05f, .state = 0.0f };

    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float wc = 2.0f * (float)M_PI * carrier_freq * t;

        // Перемноження на ортогональні несучі
        float raw_i = rf_signal[n] * cosf(wc);
        float raw_q = rf_signal[n] * (-sinf(wc));

        // Фільтрація з відновленням амплітудного масштабу (множник 2.0)
        rx_iq[n].i = 2.0f * lpf_process(&lpf_i, raw_i);
        rx_iq[n].q = 2.0f * lpf_process(&lpf_q, raw_q);
    }

    // Корекція можливого постійного зсуву
    correct_dc_offset(rx_iq, num_samples);

    printf("Контрольний відлік [100]: TX (I=%.3f, Q=%.3f) -> RX (I=%.3f, Q=%.3f)\n",
           tx_iq[100].i, tx_iq[100].q, rx_iq[100].i, rx_iq[100].q);

    free(tx_iq);
    free(rf_signal);
    free(rx_iq);
}

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PIR_SAMPLE_RATE_HZ     50
#define PIR_MIN_WINDOW_TICKS   (PIR_SAMPLE_RATE_HZ * 0.15f) // 150 мс
#define PIR_MAX_WINDOW_TICKS   (PIR_SAMPLE_RATE_HZ * 1.50f) // 1.5 с
#define PIR_DEADTIME_TICKS     (PIR_SAMPLE_RATE_HZ * 1.00f) // 1.0 с після тривоги

typedef enum {
    PIR_STATE_IDLE = 0,
    PIR_STATE_POS_PEAK_DETECTED,
    PIR_STATE_NEG_PEAK_DETECTED,
    PIR_STATE_DEADTIME
} pir_fsm_state_t;

typedef struct {
    // Коефіцієнти смугового IIR-фільтра (0.5–4.0 Гц при Fs = 50 Гц)
    float b0, b1, b2;
    float a1, a2;
    // Змінні стану фільтра (Direct Form II Transposed)
    float d1;
    float d2;

    // Адаптивний рівень шуму та поріг
    float baseline;
    float noise_sigma;
    float threshold_multiplier;

    // Стан FSM
    pir_fsm_state_t state;
    uint32_t timer_ticks;
    bool motion_detected;
} pir_processor_t;

void pir_init(pir_processor_t *p, float sensitivity_k) {
    // Коефіцієнти розраховані для Butterworth Bandpass 0.5-4.0 Гц, Fs=50 Гц
    p->b0 =  0.1983f;
    p->b1 =  0.0000f;
    p->b2 = -0.1983f;
    p->a1 = -1.5422f;
    p->a2 =  0.6034f;

    p->d1 = 0.0f;
    p->d2 = 0.0f;
    p->baseline = 0.0f;
    p->noise_sigma = 15.0f; // Початкова оцінка шуму в LSB
    p->threshold_multiplier = sensitivity_k; // Типово 3.5 - 5.0

    p->state = PIR_STATE_IDLE;
    p->timer_ticks = 0;
    p->motion_detected = false;
}

static float pir_filter_step(pir_processor_t *p, float raw_sample) {
    // Реалізація транспонованої форми Direct Form II
    float out = p->b0 * raw_sample + p->d1;
    p->d1 = p->b1 * raw_sample - p->a1 * out + p->d2;
    p->d2 = p->b2 * raw_sample - p->a2 * out;
    return out;
}

bool pir_process_sample(pir_processor_t *p, float raw_adc_sample) {
    p->motion_detected = false;

    // 1. Смугова фільтрація
    float filtered = pir_filter_step(p, raw_adc_sample);

    // 2. Адаптивне оновлення базової лінії шуму в стані спокою
    if (p->state == PIR_STATE_IDLE) {
        float abs_val = fabsf(filtered);
        // Повільне експоненційне згладжування шуму: alpha = 0.005 (~4 сек)
        p->noise_sigma = 0.995f * p->noise_sigma + 0.005f * abs_val;
        if (p->noise_sigma < 5.0f) p->noise_sigma = 5.0f; // Нижній обмежувач
    }

    float current_threshold = p->noise_sigma * p->threshold_multiplier;

    // 3. Автомат станів розпізнавання патерну
    switch (p->state) {
        case PIR_STATE_IDLE:
            if (filtered > current_threshold) {
                p->state = PIR_STATE_POS_PEAK_DETECTED;
                p->timer_ticks = 0;
            } else if (filtered < -current_threshold) {
                p->state = PIR_STATE_NEG_PEAK_DETECTED;
                p->timer_ticks = 0;
            }
            break;

        case PIR_STATE_POS_PEAK_DETECTED:
            p->timer_ticks++;
            // Очікуємо зворотного негативного піку (підтвердження руху)
            if (filtered < -current_threshold && p->timer_ticks >= PIR_MIN_WINDOW_TICKS) {
                p->motion_detected = true;
                p->state = PIR_STATE_DEADTIME;
                p->timer_ticks = 0;
            } else if (p->timer_ticks > PIR_MAX_WINDOW_TICKS) {
                // Таймаут вікна: одинична завада без другої напівхвилі
                p->state = PIR_STATE_IDLE;
            }
            break;

        case PIR_STATE_NEG_PEAK_DETECTED:
            p->timer_ticks++;
            // Очікуємо зворотного позитивного піку
            if (filtered > current_threshold && p->timer_ticks >= PIR_MIN_WINDOW_TICKS) {
                p->motion_detected = true;
                p->state = PIR_STATE_DEADTIME;
                p->timer_ticks = 0;
            } else if (p->timer_ticks > PIR_MAX_WINDOW_TICKS) {
                p->state = PIR_STATE_IDLE;
            }
            break;

        case PIR_STATE_DEADTIME:
            p->timer_ticks++;
            // Період блокування повторних спрацьовувань після тривоги
            if (p->timer_ticks >= PIR_DEADTIME_TICKS) {
                p->state = PIR_STATE_IDLE;
            }
            break;
    }

    return p->motion_detected;
}

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAMPLE_RATE_HZ       100
#define ADC_MAX_VAL          4095
#define ADC_VREF_MV          3300

/* Параметри адаптивного віконного компаратора */
#define DEFAULT_BASELINE_ADC 2048
#define THRESHOLD_OFFSET_ADC 350
#define MIN_PULSE_WIDTH_MS   100
#define MAX_PULSE_WIDTH_MS   1500
#define MOTION_WINDOW_MS     2500

typedef enum {
    PIR_STATE_IDLE = 0,
    PIR_STATE_POS_PEAK_DETECTED,
    PIR_STATE_NEG_PEAK_DETECTED,
    PIR_STATE_MOTION_CONFIRMED
} pir_state_t;

typedef struct {
    float baseline;
    float alpha_baseline;  /* Коефіцієнт згладжування нульової лінії */
    float iir_filtered;
    float alpha_lp;        /* Коефіцієнт ФНЧ (5 Гц) */
    
    pir_state_t state;
    uint32_t state_timer_ms;
    uint32_t last_peak_time_ms;
    
    uint16_t pos_threshold;
    uint16_t neg_threshold;
} pir_detector_t;

void pir_detector_init(pir_detector_t *det) {
    det->baseline = (float)DEFAULT_BASELINE_ADC;
    det->alpha_baseline = 0.005f; /* Дуже повільний дрейф нульової точки (~0.05 Гц) */
    det->iir_filtered = (float)DEFAULT_BASELINE_ADC;
    det->alpha_lp = 0.24f;        /* Срез ФНЧ на рівні ~5 Гц при f_s = 100 Гц */
    
    det->state = PIR_STATE_IDLE;
    det->state_timer_ms = 0;
    det->last_peak_time_ms = 0;
    
    det->pos_threshold = DEFAULT_BASELINE_ADC + THRESHOLD_OFFSET_ADC;
    det->neg_threshold = DEFAULT_BASELINE_ADC - THRESHOLD_OFFSET_ADC;
}

bool pir_detector_process_sample(pir_detector_t *det, uint16_t raw_adc, uint32_t current_time_ms) {
    /* 1. Цифрова ФНЧ-фільтрація першого порядку (придушення 50 Гц та шуму АЦП) */
    det->iir_filtered += det->alpha_lp * ((float)raw_adc - det->iir_filtered);
    
    /* 2. Адаптивне відстеження нульової лінії (базової лінії) */
    /* Оновлюємо базову лінію лише тоді, коли відсутні сплески сигналу */
    float diff = fabsf(det->iir_filtered - det->baseline);
    if (diff < (float)(THRESHOLD_OFFSET_ADC / 2)) {
        det->baseline += det->alpha_baseline * (det->iir_filtered - det->baseline);
        det->pos_threshold = (uint16_t)(det->baseline + THRESHOLD_OFFSET_ADC);
        det->neg_threshold = (uint16_t)(det->baseline - THRESHOLD_OFFSET_ADC);
    }

    float sig = det->iir_filtered;
    bool motion_detected = false;

    /* 3. Автомат скінченних станів для розпізнавання дуального піку (перетинання 2 зон) */
    switch (det->state) {
        case PIR_STATE_IDLE:
            if (sig > (float)det->pos_threshold) {
                det->state = PIR_STATE_POS_PEAK_DETECTED;
                det->last_peak_time_ms = current_time_ms;
            } else if (sig < (float)det->neg_threshold) {
                det->state = PIR_STATE_NEG_PEAK_DETECTED;
                det->last_peak_time_ms = current_time_ms;
            }
            break;

        case PIR_STATE_POS_PEAK_DETECTED:
            /* Очікуємо протилежну напівхвилю (негативний пік) у межах часового вікна */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE; /* Таймаут — поодинока завада */
            } else if (sig < (float)det->neg_threshold) {
                uint32_t delta = current_time_ms - det->last_peak_time_ms;
                if (delta >= MIN_PULSE_WIDTH_MS && delta <= MAX_PULSE_WIDTH_MS) {
                    det->state = PIR_STATE_MOTION_CONFIRMED;
                    motion_detected = true;
                }
            }
            break;

        case PIR_STATE_NEG_PEAK_DETECTED:
            /* Очікуємо позитивний пік */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE;
            } else if (sig > (float)det->pos_threshold) {
                uint32_t delta = current_time_ms - det->last_peak_time_ms;
                if (delta >= MIN_PULSE_WIDTH_MS && delta <= MAX_PULSE_WIDTH_MS) {
                    det->state = PIR_STATE_MOTION_CONFIRMED;
                    motion_detected = true;
                }
            }
            break;

        case PIR_STATE_MOTION_CONFIRMED:
            /* Утримання сигналу тривоги та пауза усунення повторних спрацьовувань */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE;
            }
            break;
    }

    return motion_detected;
}

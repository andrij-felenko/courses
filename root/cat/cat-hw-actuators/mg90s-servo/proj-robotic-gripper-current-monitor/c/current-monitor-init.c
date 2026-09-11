#include <stdint.h>
#include <stdbool.h>

#define BLANKING_TIME_MS       30    // Тривалість вікна стробування (мс)
#define SAMPLE_INTERVAL_MS     2     // Період виклику обробника (мс)
#define EMA_ALPHA_Q8           26    // Коефіцієнт EMA (0.10 * 256)
#define DERIV_HISTORY_LEN      4     // Довжина буфера для dI/dt (4 * 2 мс = 8 мс)
#define DERIV_THRESHOLD_MA_MS  30    // Поріг швидкості наростання (мА/мс)
#define STALL_CURRENT_MAX_MA   750   // Абсолютний поріг заклинювання (мА)

typedef struct {
    uint32_t blanking_timer_ms;      // Таймер вікна стробування
    bool is_blanking;                // Прапорець активного стробування
    int32_t current_filtered_q8;     // Фільтрований струм у форматі Q8
    uint16_t history[DERIV_HISTORY_LEN]; // Кільцевий буфер історії струму
    uint8_t history_idx;             // Поточний індекс у буфері
    bool contact_detected;           // Прапорець виявлення контакту
} CurrentMonitor;

void current_monitor_init(CurrentMonitor *mon) {
    mon->blanking_timer_ms = 0;
    mon->is_blanking = false;
    mon->current_filtered_q8 = 0;
    mon->history_idx = 0;
    mon->contact_detected = false;
    for (int i = 0; i < DERIV_HISTORY_LEN; i++) {
        mon->history[i] = 0;
    }
}

// Викликається під час видачі нової позиції сервоприводу
void current_monitor_on_motion_start(CurrentMonitor *mon) {
    mon->blanking_timer_ms = BLANKING_TIME_MS;
    mon->is_blanking = true;
    mon->contact_detected = false;
}

// Періодичний крок обробки (викликається кожні 2 мс за таймером)
void current_monitor_process(CurrentMonitor *mon, uint16_t raw_adc_ma) {
    // 1. Оновлення таймера стробування
    if (mon->is_blanking) {
        if (mon->blanking_timer_ms > SAMPLE_INTERVAL_MS) {
            mon->blanking_timer_ms -= SAMPLE_INTERVAL_MS;
        } else {
            mon->blanking_timer_ms = 0;
            mon->is_blanking = false;
        }
    }

    // 2. Експоненційне згладжування (EMA) у форматі Q8
    int32_t raw_q8 = (int32_t)raw_adc_ma << 8;
    mon->current_filtered_q8 = (EMA_ALPHA_Q8 * raw_q8 + 
                                (256 - EMA_ALPHA_Q8) * mon->current_filtered_q8) >> 8;
    uint16_t current_ma = (uint16_t)(mon->current_filtered_q8 >> 8);

    // 3. Обчислення похідної dI/dt за кільцевим буфером
    uint8_t oldest_idx = (mon->history_idx + 1) % DERIV_HISTORY_LEN;
    uint16_t past_current = mon->history[oldest_idx];
    
    // Збереження поточного відліку в буфер
    mon->history[mon->history_idx] = current_ma;
    mon->history_idx = oldest_idx;

    int16_t delta_i = (int16_t)current_ma - (int16_t)past_current;
    // delta_t = DERIV_HISTORY_LEN * SAMPLE_INTERVAL_MS = 8 мс
    int16_t di_dt = delta_i / (DERIV_HISTORY_LEN * SAMPLE_INTERVAL_MS);

    // 4. Детектування контакту (лише поза вікном стробування)
    if (!mon->is_blanking) {
        if (di_dt >= DERIV_THRESHOLD_MA_MS || current_ma >= STALL_CURRENT_MAX_MA) {
            mon->contact_detected = true;
        }
    }
}

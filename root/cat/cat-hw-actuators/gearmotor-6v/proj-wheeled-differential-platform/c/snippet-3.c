#include <stdint.h>
#include <stdbool.h>

// Структура параметрів калібрування та поточного стану струмового тракту
typedef struct {
    uint16_t adc_zero;         // Зміщення нуля АЦП (відліки)
    uint32_t k_scale_fp;       // Коефіцієнт масштабування у форматі Q16 (мА/відлік)
    uint16_t trip_current_ma;  // Поріг струмового захисту (мА)
    uint8_t  overcurrent_cnt;  // Лічильник безперервних перевищень порогу
    bool     fault_latched;    // Прапорець зафіксованої аварії
} CurrentMonitor;

// Ініціалізація та калібрування зміщення нуля за відсутності струму
void CurrentMonitor_CalibrateZero(CurrentMonitor *mon, uint16_t (*read_adc_fn)(void)) {
    uint32_t sum = 0;
    const uint16_t samples = 128;

    for (uint16_t i = 0; i < samples; i++) {
        sum += read_adc_fn();
    }
    mon->adc_zero = (uint16_t)(sum / samples);
    mon->overcurrent_cnt = 0;
    mon->fault_latched = false;
}

// Обчислення коефіцієнта масштабування за еталонним струмом
void CurrentMonitor_CalibrateScale(CurrentMonitor *mon, uint16_t adc_cal, uint16_t ref_current_ma) {
    if (adc_cal > mon->adc_zero) {
        uint32_t span = adc_cal - mon->adc_zero;
        // Масштабуємо ціну поділки в Q16: (I_ref * 65536) / span
        mon->k_scale_fp = ((uint32_t)ref_current_ma << 16) / span;
    }
}

// Періодична перевірка струму (викликається в таймері кожні 2 мс)
// Повертає true, якщо зафіксовано заклинювання і ШІМ необхідно зняти
bool CurrentMonitor_Update(CurrentMonitor *mon, uint16_t raw_adc) {
    if (mon->fault_latched) {
        return true;
    }

    uint16_t net_adc = (raw_adc > mon->adc_zero) ? (raw_adc - mon->adc_zero) : 0;
    uint32_t current_ma = ((uint32_t)net_adc * mon->k_scale_fp) >> 16;

    // Перевірка перевищення робочого порогу
    if (current_ma >= mon->trip_current_ma) {
        if (mon->overcurrent_cnt < 5) {
            mon->overcurrent_cnt++;
        } else {
            mon->fault_latched = true; // 5 вибірок по 2 мс = 10 мс підтвердження
            return true;
        }
    } else {
        if (mon->overcurrent_cnt > 0) {
            mon->overcurrent_cnt--; // Захист від випадкових сплесків
        }
    }

    return false;
}

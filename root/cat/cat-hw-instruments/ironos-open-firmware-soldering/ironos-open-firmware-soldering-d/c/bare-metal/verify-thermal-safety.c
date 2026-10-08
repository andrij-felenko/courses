#include <stdint.h>
#include <stdbool.h>

typedef enum {
    THERMAL_STATE_OK = 0,
    THERMAL_STATE_ERROR_NO_TIP,
    THERMAL_STATE_ERROR_RUNAWAY,
    THERMAL_STATE_ERROR_MOSFET_SHORT
} thermal_state_t;

typedef struct {
    int16_t temp_meas_c;      // Поточна виміряна температура в градусах Цельсія
    int16_t temp_set_c;       // Задана температура в градусах Цельсія
    uint8_t pwm_duty;         // Поточне заповнення ШІМ (0..255)
    uint16_t adc_raw;         // Сире значення АЦП
} thermal_inputs_t;

thermal_state_t verify_thermal_safety(const thermal_inputs_t* in, uint32_t dt_ms) {
    static uint32_t runaway_timer_ms = 0;

    // 1. Перевірка на обрив термопари (АЦП у верхньому насиченні > 4000 або температура > 500 °C)
    if (in->adc_raw > 4000 || in->temp_meas_c > 500 || in->temp_meas_c < -10) {
        runaway_timer_ms = 0;
        return THERMAL_STATE_ERROR_NO_TIP;
    }

    // 2. Перевірка на терморозгін при високому заповненні ШІМ
    if (in->pwm_duty > 200 && (in->temp_set_c - in->temp_meas_c) > 30) {
        runaway_timer_ms += dt_ms;
        if (runaway_timer_ms > 5000) { // Якщо температура не піднімається 5 секунд при 80%+ ШІМ
            return THERMAL_STATE_ERROR_RUNAWAY;
        }
    } else {
        if (runaway_timer_ms >= dt_ms) {
            runaway_timer_ms -= dt_ms;
        } else {
            runaway_timer_ms = 0;
        }
    }

    return THERMAL_STATE_OK;
}

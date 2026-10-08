#include <stdint.h>
#include <stdbool.h>

// Структура стану витратоміра для чисельного інтегрування
typedef struct {
    float k_factor_pulses_per_liter; // K-фактор (імпульсів на літр)
    float last_flow_rate_lpm;        // Попередня миттєва витрата (л/хв)
    uint64_t last_timestamp_us;       // Час попереднього відліку (мікросекунди)
    float total_volume_liters;       // Накопичений об'єм (літри)
} flow_meter_t;

void flow_meter_init(flow_meter_t *meter, float k_factor) {
    meter->k_factor_pulses_per_liter = k_factor;
    meter->last_flow_rate_lpm = 0.0f;
    meter->last_timestamp_us = 0;
    meter->total_volume_liters = 0.0f;
}

// Оновлення обчислення витрати та інтегрування об'єму за методом трапецій
void flow_meter_update(flow_meter_t *meter, uint32_t pulse_count, uint64_t current_timestamp_us) {
    if (meter->last_timestamp_us == 0) {
        meter->last_timestamp_us = current_timestamp_us;
        return;
    }

    // Тривалість інтервалу дискретизації в секундах
    float dt_sec = (float)(current_timestamp_us - meter->last_timestamp_us) / 1000000.0f;
    if (dt_sec <= 0.0f) return;

    // Поточна частота імпульсів (Гц)
    float frequency_hz = (float)pulse_count / dt_sec;

    // Поточна миттєва витрата у літрах за хвилину (л/хв)
    float current_flow_rate_lpm = (frequency_hz * 60.0f) / meter->k_factor_pulses_per_liter;

    // Миттєва витрата у літрах за секунду (л/с) для інтегрування
    float current_flow_lps = current_flow_rate_lpm / 60.0f;
    float last_flow_lps = meter->last_flow_rate_lpm / 60.0f;

    // Числове інтегрування методом трапецій: ΔV = ((Q_prev + Q_curr) / 2) * Δt
    float delta_volume_liters = ((last_flow_lps + current_flow_lps) / 2.0f) * dt_sec;

    meter->total_volume_liters += delta_volume_liters;
    meter->last_flow_rate_lpm = current_flow_rate_lpm;
    meter->last_timestamp_us = current_timestamp_us;
}

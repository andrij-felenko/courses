#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATION_STATUS_OK = 0,
    STATION_ERROR_SE  = 1, // Sensor Error (обрив/КЗ термопари)
    STATION_ERROR_HE  = 2  // Heater Error (несправність нагрівача)
} station_status_t;

station_status_t evaluate_station_safety(uint16_t adc_val, float current_temp, float target_temp, uint32_t active_heating_ticks) {
    // 1. Перевірка виходу ADC за допустимий межевий діапазон (Обрив або КЗ)
    if (adc_val < 15 || adc_val > 1005) {
        return STATION_ERROR_SE;
    }

    // 2. Перевірка наявності динаміки нагріву при активній подачі живлення
    if (active_heating_ticks > 600 && (target_temp - current_temp > 45.0f)) {
        return STATION_ERROR_HE;
    }

    return STATION_STATUS_OK;
}

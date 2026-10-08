#include <stdint.h>

// Перетворення коду S_T у соті частки градуса Цельсія (наприклад, 2350 = 23.50 °C)
int32_t sht30_convert_temp_celsius_x100(uint16_t raw_temp) {
    int32_t numerator = (int32_t)17500 * raw_temp + 32767;
    return -4500 + (numerator / 65535);
}

// Перетворення коду S_T у соті частки градуса Фаренгейта (наприклад, 7430 = 74.30 °F)
int32_t sht30_convert_temp_fahrenheit_x100(uint16_t raw_temp) {
    int32_t numerator = (int32_t)31500 * raw_temp + 32767;
    return -4900 + (numerator / 65535);
}

// Перетворення коду S_RH у соті частки відсотка вологості (наприклад, 5540 = 55.40 % RH)
uint16_t sht30_convert_humidity_x100(uint16_t raw_humidity) {
    uint32_t numerator = (uint32_t)10000 * raw_humidity + 32767;
    uint32_t rh = numerator / 65535;
    
    // Обмеження діапазону 0..10000 (0.00% .. 100.00%)
    if (rh > 10000) {
        rh = 10000;
    }
    return (uint16_t)rh;
}

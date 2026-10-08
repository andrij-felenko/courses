#include <Arduino.h>

struct AHT20Values {
    float humidity;     // %
    float temperature;  // °C
};

struct AHT20FixedValues {
    int32_t humidity_x100;    // соті % (наприклад, 4520 = 45.20%)
    int32_t temperature_x100; // соті °C (наприклад, 2350 = 23.50°C)
};

AHT20Values calculateFloat(uint32_t s_rh, uint32_t s_t) {
    AHT20Values val;
    val.humidity = ((float)s_rh * 100.0f) / 1048576.0f;
    val.temperature = ((float)s_t * 200.0f) / 1048576.0f - 50.0f;
    return val;
}

AHT20FixedValues calculateFixed(uint32_t s_rh, uint32_t s_t) {
    AHT20FixedValues val;
    // uint64_t гарантує відсутність переповнення при множенні на 10000 / 20000
    val.humidity_x100 = (int32_t)(((uint64_t)s_rh * 10000ULL) >> 20);
    val.temperature_x100 = (int32_t)((((uint64_t)s_t * 20000ULL) >> 20) - 5000);
    return val;
}

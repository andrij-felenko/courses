#include <math.h>
#include <stdint.h>

// Емпіричні коефіцієнти формули Магнуса-Тетенса
#define MAGNUS_A 6.112f
#define MAGNUS_B 17.67f
#define MAGNUS_C 243.5f

// Структура фізичних даних з давача AHT20
typedef struct {
    float temperature;
    float humidity;
} aht20_data_t;

// Декодування сирих 20-бітних даних AHT20
aht20_data_t aht20_decode_raw(uint32_t raw_humidity, uint32_t raw_temp) {
    aht20_data_t result;
    result.humidity = ((float)raw_humidity / 1048576.0f) * 100.0f;
    result.temperature = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;
    return result;
}

// Розрахунок точки роси з плаваючою комою
float calculate_dew_point_fp(float temp_c, float humidity_rh) {
    if (humidity_rh <= 0.0f || humidity_rh > 100.0f) {
        return -999.0f; // Захист від некоректних даних
    }
    float gamma = logf(humidity_rh / 100.0f) + (MAGNUS_B * temp_c) / (MAGNUS_C + temp_c);
    float dew_point = (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
    return dew_point;
}

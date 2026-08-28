#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Структура виміряних параметрів мікроклімату
typedef struct {
    float temperature_c;     // Температура повітря, °C
    float relative_humidity; // Відносна вологість, % RH
    float dew_point_c;       // Розрахована точка роси, °C
} climate_sample_t;

// Обчислення точки роси за формулою Магнуса
float calculate_dew_point(float temp_c, float rh_pct) {
    const float b = 17.62f;
    const float c = 243.12f;
    if (rh_pct < 0.1f) rh_pct = 0.1f;
    if (rh_pct > 100.0f) rh_pct = 100.0f;
    
    float gamma = logf(rh_pct / 100.0f) + (b * temp_c) / (c + temp_c);
    return (c * gamma) / (b - gamma);
}

// Конвертація 16-бітних сирих слів SHT4x у фізичні одиниці
bool parse_sht4x_raw(uint16_t raw_temp, uint16_t raw_rh, climate_sample_t *out) {
    if (!out) return false;
    
    // Формули згідно зі специфікацією Sensirion SHT4x
    out->temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    
    float rh = -6.0f + 125.0f * ((float)raw_rh / 65535.0f);
    if (rh < 0.0f) rh = 0.0f;
    if (rh > 100.0f) rh = 100.0f;
    out->relative_humidity = rh;
    
    out->dew_point_c = calculate_dew_point(out->temperature_c, out->relative_humidity);
    return true;
}

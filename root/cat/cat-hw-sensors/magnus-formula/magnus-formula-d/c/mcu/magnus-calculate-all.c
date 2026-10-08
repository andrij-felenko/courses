#include <math.h>
#include <stdbool.h>

// Структура результатів обчислення мікрокліматичних параметрів
typedef struct {
    float saturation_pressure_hpa; // Тиск насиченої пари E(t) [hPa]
    float vapor_pressure_hpa;      // Поточний парціальний тиск e [hPa]
    float dew_point_c;             // Точка роси T_d [°C]
    float absolute_humidity_gm3;   // Абсолютна вологість AH [g/m³]
    bool is_valid;                 // Прапорець успішності обчислення
} magnus_results_t;

// Обчислення повного набору параметрів вологого повітря
magnus_results_t magnus_calculate_all(float temp_c, float rh_percent) {
    magnus_results_t res = {0};

    // Перевірка допустимих меж вимірювань давача
    if (rh_percent < 0.1f || rh_percent > 100.0f || temp_c < -40.0f || temp_c > 100.0f) {
        res.is_valid = false;
        res.dew_point_c = NAN;
        return res;
    }

    // Вибір коефіцієнтів WMO залежно від фазового стану (вода / лід)
    const float a = 6.112f;
    const float b = (temp_c >= 0.0f) ? 17.625f : 22.46f;
    const float c = (temp_c >= 0.0f) ? 243.04f : 272.62f;

    // 1. Обчислення тиску насичення E(t) з використанням 32-бітної expf()
    res.saturation_pressure_hpa = a * expf((b * temp_c) / (c + temp_c));

    // 2. Обчислення поточного парціального тиску e
    float rh_fraction = rh_percent / 100.0f;
    res.vapor_pressure_hpa = rh_fraction * res.saturation_pressure_hpa;

    // 3. Обчислення проміжної функції gamma з використанням 32-бітної logf()
    float gamma = (b * temp_c) / (c + temp_c) + logf(rh_fraction);

    // Захист від ділення на нуль при gamma == b
    float denominator = b - gamma;
    if (fabsf(denominator) < 1e-6f) {
        res.is_valid = false;
        res.dew_point_c = NAN;
        return res;
    }

    // 4. Обчислення точки роси T_d
    res.dew_point_c = (c * gamma) / denominator;

    // 5. Обчислення абсолютної вологості AH [g/m³]
    res.absolute_humidity_gm3 = 216.7f * (res.vapor_pressure_hpa / (273.15f + temp_c));

    res.is_valid = true;
    return res;
}

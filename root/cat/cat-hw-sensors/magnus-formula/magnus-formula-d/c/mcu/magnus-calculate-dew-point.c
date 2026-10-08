#include <math.h>

// Розрахунок точки роси за формулою Магнуса-Тетенса (C)
float magnus_calculate_dew_point(float temp_c, float rh_percent) {
    if (rh_percent <= 0.0f || rh_percent > 100.0f) {
        return NAN; // Перевірка коректності вхідних даних вологості
    }

    // Вибір коефіцієнтів залежно від знаку температури (вода / лід)
    float b = (temp_c >= 0.0f) ? 17.625f : 22.46f;
    float c = (temp_c >= 0.0f) ? 243.04f : 272.62f;

    // Розрахунок проміжної функції gamma
    float rh_fraction = rh_percent / 100.0f;
    float gamma = (b * temp_c) / (c + temp_c) + logf(rh_fraction);

    // Розрахунок точки роси
    float dew_point = (c * gamma) / (b - gamma);
    return dew_point;
}

#include <math.h>
#include <stdbool.h>

// Коефіцієнти Магнуса-Тетенса (за стандартом Sonntag)
#define MAGNUS_A 17.625f
#define MAGNUS_B 243.04f

/**
 * Обчислення температури точки роси у градусах Цельсія.
 * @param temp_c Температура повітря, °C
 * @param rh_percent Відносна вологість повітря, % (0.1 - 100.0)
 * @param[out] dew_point_c Указник для збереження результату, °C
 * @return true якщо обчислення успішне, false при некоректних вхідних даних
 */
bool calculate_dew_point_c(float temp_c, float rh_percent, float *dew_point_c) {
    if (rh_percent <= 0.0f || rh_percent > 100.0f || dew_point_c == NULL) {
        return false;
    }

    // Захист від від'ємного знаменника в алгоритмі
    float alpha = (MAGNUS_A * temp_c) / (MAGNUS_B + temp_c);
    float gamma = logf(rh_percent / 100.0f) + alpha;

    float denominator = MAGNUS_A - gamma;
    if (fabsf(denominator) < 1e-6f) {
        return false;
    }

    *dew_point_c = (MAGNUS_B * gamma) / denominator;
    return true;
}

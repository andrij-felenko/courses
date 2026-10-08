#include <math.h>
#include <stdbool.h>

// Коефіцієнти стандарту IEC 60751 для платинових RTD (α = 0.003851)
#define RTD_PARAM_A  3.9083e-3f
#define RTD_PARAM_B -5.775e-7f

/**
 * @brief Обчислення точної температури для діапазону t >= 0 °C за формулою Каллендара — Ван Дюзена.
 * 
 * @param r_measured Виміряний опір RTD у Омах.
 * @param r0 Номінальний опір датчика при 0 °C (наприклад, 100.0f для PT100).
 * @param[out] temp_out Вказівник на змінну для збереження обчисленої температури в °C.
 * @return true якщо опір відповідає діапазону t >= 0 °C, false у разі некоректних даних.
 */
bool rtd_calculate_temp_positive(float r_measured, float r0, float *temp_out) {
    if (temp_out == NULL || r0 <= 0.0f || r_measured < r0) {
        return false;
    }

    float z = 1.0f - (r_measured / r0);
    float discriminant = (RTD_PARAM_A * RTD_PARAM_A) - (4.0f * RTD_PARAM_B * z);

    if (discriminant < 0.0f) {
        return false;
    }

    *temp_out = (-RTD_PARAM_A + sqrtf(discriminant)) / (2.0f * RTD_PARAM_B);
    return true;
}

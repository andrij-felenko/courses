#include <Arduino.h>
#include <math.h>

class RtdPt100Calculator {
public:
    static constexpr float PARAM_A = 3.9083e-3f;
    static constexpr float PARAM_B = -5.775e-7f;

    /**
     * @brief Обчислює точну температуру (°C) за виміряним опором для t >= 0 °C.
     * @param rMeasured Виміряний опір датчика в Омах.
     * @param r0 Номінальний опір при 0 °C (за замовчуванням 100.0 Ом).
     * @return Температура в °C або NAN при від'ємній температурі чи помилці.
     */
    static float calculateTempPositive(float rMeasured, float r0 = 100.0f) {
        if (rMeasured < r0 || r0 <= 0.0f) {
            return NAN;
        }

        const float z = 1.0f - (rMeasured / r0);
        const float discriminant = (PARAM_A * PARAM_A) - (4.0f * PARAM_B * z);

        if (discriminant < 0.0f) {
            return NAN;
        }

        return (-PARAM_A + sqrtf(discriminant)) / (2.0f * PARAM_B);
    }
};

#include <cmath>

class PlatinumRTD {
public:
    static constexpr float R0 = 100.0f;
    static constexpr float A  = 3.9083e-3f;
    static constexpr float B  = -5.775e-7f;

    // Обчислення температури для додатного діапазону (t >= 0 °C)
    static float resistanceToTemperature(float rMeasured) {
        if (rMeasured < R0) {
            return -1.0f; // Сигнал для переходу до кріогенного алгоритму
        }

        const float ratio = rMeasured / R0;
        const float discriminant = (A * A) - (4.0f * B * (1.0f - ratio));
        
        return (-A + std::sqrt(discriminant)) / (2.0f * B);
    }
};

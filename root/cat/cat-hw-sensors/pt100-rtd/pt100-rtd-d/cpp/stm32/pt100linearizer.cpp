#include <cmath>
#include <cstdint>

class Pt100Linearizer {
public:
    static constexpr float R0 = 100.0f;
    static constexpr float A  = 3.9083e-3f;
    static constexpr float B  = -5.775e-7f;

    // Обчислення температури з використанням апаратного FPU
    static float toCelsius(float rMeasured) noexcept {
        if (rMeasured < R0) {
            return (rMeasured - R0) / (R0 * A);
        }
        const float polyC = 1.0f - (rMeasured / R0);
        const float discriminant = (A * A) - (4.0f * B * polyC);
        return (-A + std::sqrt(discriminant)) / (2.0f * B);
    }
};

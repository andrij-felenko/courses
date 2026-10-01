#include <cmath>
#include <optional>

class ClimateMath {
public:
    static constexpr float MAGNUS_A = 17.27f;
    static constexpr float MAGNUS_B = 237.7f;

    // Обчислення точки роси з поверненням optional
    static std::optional<float> calculateDewPoint(float tempC, float rhPct) noexcept {
        if (rhPct <= 0.0f || rhPct > 100.0f || tempC < -40.0f || tempC > 85.0f) {
            return std::nullopt;
        }
        const float gamma = (MAGNUS_A * tempC) / (MAGNUS_B + tempC) + std::log(rhPct / 100.0f);
        return (MAGNUS_B * gamma) / (MAGNUS_A - gamma);
    }

    // Обчислення висоти щодо опорного тиску QNH
    static float calculateAltitude(float pressureHpa, float qnhHpa = 1013.25f) noexcept {
        if (qnhHpa <= 0.0f || pressureHpa <= 0.0f) {
            return 0.0f;
        }
        const float ratio = pressureHpa / qnhHpa;
        return 44330.77f * (1.0f - std::pow(ratio, 0.190263f));
    }
};

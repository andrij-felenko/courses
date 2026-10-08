#include <cmath>
#include <optional>

class EnvironmentalPsychrometrics {
public:
    static constexpr float MAGNUS_A = 17.625f;
    static constexpr float MAGNUS_B = 243.04f;

    /**
     * Обчислює точку роси T_dp за виміряними T та RH.
     */
    static std::optional<float> calculateDewPoint(float tempC, float rhPercent) noexcept {
        if (rhPercent <= 0.0f || rhPercent > 100.0f) {
            return std::nullopt;
        }

        const float alpha = (MAGNUS_A * tempC) / (MAGNUS_B + tempC);
        const float gamma = std::log(rhPercent / 100.0f) + alpha;

        const float denominator = MAGNUS_A - gamma;
        if (std::abs(denominator) < 1e-6f) {
            return std::nullopt;
        }

        return (MAGNUS_B * gamma) / denominator;
    }
};

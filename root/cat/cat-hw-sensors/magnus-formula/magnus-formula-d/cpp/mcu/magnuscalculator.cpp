#include <cmath>
#include <limits>

namespace Climate {

class MagnusCalculator {
public:
    // Розрахунок точки роси для мікроконтролера (C++)
    static float calculateDewPoint(float tempC, float rhPercent) noexcept {
        if (rhPercent <= 0.0f || rhPercent > 100.0f) {
            return std::numeric_limits<float>::quiet_NaN();
        }

        const float b = (tempC >= 0.0f) ? 17.625f : 22.46f;
        const float c = (tempC >= 0.0f) ? 243.04f : 272.62f;

        const float rhFraction = rhPercent / 100.0f;
        const float gamma = (b * tempC) / (c + tempC) + std::log(rhFraction);

        return (c * gamma) / (b - gamma);
    }
};

} // namespace Climate

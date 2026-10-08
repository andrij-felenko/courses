#include <cmath>
#include <optional>
#include <limits>

namespace Climate {

struct AirState {
    float saturationPressureHpa;
    float vaporPressureHpa;
    float dewPointC;
    float absoluteHumidityGm3;
};

class MagnusEngine {
public:
    // Обчислення параметрів вологого повітря на вбудованій платформі (C++)
    static std::optional<AirState> calculate(float tempC, float rhPercent) noexcept {
        if (rhPercent < 0.1f || rhPercent > 100.0f || tempC < -40.0f || tempC > 100.0f) {
            return std::nullopt;
        }

        constexpr float a = 6.112f;
        const float b = (tempC >= 0.0f) ? 17.625f : 22.46f;
        const float c = (tempC >= 0.0f) ? 243.04f : 272.62f;

        const float satPres = a * std::exp((b * tempC) / (c + tempC));
        const float rhFrac = rhPercent / 100.0f;
        const float vapPres = rhFrac * satPres;

        const float gamma = (b * tempC) / (c + tempC) + std::log(rhFrac);
        const float denom = b - gamma;

        if (std::abs(denom) < 1e-6f) {
            return std::nullopt;
        }

        const float dewPoint = (c * gamma) / denom;
        const float absHum = 216.7f * (vapPres / (273.15f + tempC));

        return AirState{satPres, vapPres, dewPoint, absHum};
    }
};

} // namespace Climate

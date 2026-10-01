#include <cmath>

float calculateDewPoint(float temp, float humidity) {
    constexpr float b = 17.67f;
    constexpr float c = 243.5f;
    float gamma = std::log(humidity / 100.0f) + (b * temp) / (c + temp);
    return (c * gamma) / (b - gamma);
}

float calculateAbsoluteHumidity(float temp, float humidity) {
    constexpr float a = 6.112f;
    constexpr float b = 17.67f;
    constexpr float c = 243.5f;
    float pS = a * std::exp((b * temp) / (c + temp));
    float pA = pS * (humidity / 100.0f);
    return (216.7f * pA) / (273.15f + temp);
}

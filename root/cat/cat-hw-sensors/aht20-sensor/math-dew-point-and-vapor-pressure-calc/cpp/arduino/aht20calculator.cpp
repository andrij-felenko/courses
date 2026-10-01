#include <Arduino.h>
#include <math.h>

class AHT20Calculator {
private:
    static constexpr float MAGNUS_B = 17.67f;
    static constexpr float MAGNUS_C = 243.5f;

public:
    static float rawToHumidity(uint32_t rawHumidity) {
        return (static_cast<float>(rawHumidity) / 1048576.0f) * 100.0f;
    }

    static float rawToTemperature(uint32_t rawTemp) {
        return (static_cast<float>(rawTemp) / 1048576.0f) * 200.0f - 50.0f;
    }

    static float calculateDewPoint(float tempC, float humidityRH) {
        if (humidityRH <= 0.0f) return -999.0f;
        float gamma = logf(humidityRH / 100.0f) + (MAGNUS_B * tempC) / (MAGNUS_C + tempC);
        return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
    }
};

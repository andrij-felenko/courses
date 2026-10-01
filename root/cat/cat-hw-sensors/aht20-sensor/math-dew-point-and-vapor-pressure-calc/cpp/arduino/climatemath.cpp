#include <Arduino.h>
#include <math.h>

class ClimateMath {
public:
    static constexpr float MAGNUS_A = 6.112f;
    static constexpr float MAGNUS_B = 17.62f;
    static constexpr float MAGNUS_C = 243.12f;

    static float dewPoint(float tempC, float humidityRH) {
        if (humidityRH <= 0.0f) return -999.0f;
        
        float gamma = logf(humidityRH / 100.0f) + (MAGNUS_B * tempC) / (MAGNUS_C + tempC);
        return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
    }

    static float absoluteHumidity(float tempC, float humidityRH) {
        if (humidityRH <= 0.0f) return 0.0f;
        
        float e_s = MAGNUS_A * expf((MAGNUS_B * tempC) / (MAGNUS_C + tempC));
        float e = e_s * (humidityRH / 100.0f);
        return (216.679f * e) / (tempC + 273.15f);
    }
};

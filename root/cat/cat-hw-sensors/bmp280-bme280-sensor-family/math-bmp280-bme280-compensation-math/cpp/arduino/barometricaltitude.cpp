#include <Arduino.h>

class BarometricAltitude {
public:
    static float getAltitude(float pressurePa, float seaLevelHpa = 1013.25f) {
        float pressureHpa = pressurePa / 100.0f;
        if (pressureHpa <= 0.0f) return 0.0f;
        return 44330.77f * (1.0f - pow(pressureHpa / seaLevelHpa, 0.19029495));
    }

    static float getRelativeHeight(float currentPressurePa, float startPressurePa, float tempC = 15.0f) {
        if (currentPressurePa <= 0.0f || startPressurePa <= 0.0f) return 0.0f;
        float h_raw = 44330.77f * (1.0f - pow(currentPressurePa / startPressurePa, 0.19029495));
        float tempK = tempC + 273.15f;
        return h_raw * (tempK / 288.15f);
    }
};

#include <Arduino.h>

bool updateAntiCondensationHeater(float tempSurface, float dewPoint, bool currentHeaterState) {
    constexpr float kMarginOn = 3.0f;
    constexpr float kMarginOff = 6.0f;

    float thresholdOn = dewPoint + kMarginOn;
    float thresholdOff = dewPoint + kMarginOff;

    if (tempSurface <= thresholdOn) {
        return true;
    } else if (tempSurface >= thresholdOff) {
        return false;
    }

    return currentHeaterState;
}

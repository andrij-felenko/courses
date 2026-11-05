#include "HeaterController.hpp"

HeaterController::HeaterController(float hysteresisC, float safetyMarginC)
    : hysteresisC_(hysteresisC), safetyMarginC_(safetyMarginC) {}

void HeaterController::update(float currentTemp, float dewPoint) {
    float targetMin = dewPoint + safetyMarginC_;
    float targetMax = targetMin + hysteresisC_;

    if (currentTemp <= targetMin) {
        isOn_ = true;
    } else if (currentTemp >= targetMax) {
        isOn_ = false;
    }
}

bool HeaterController::isOn() const {
    return isOn_;
}

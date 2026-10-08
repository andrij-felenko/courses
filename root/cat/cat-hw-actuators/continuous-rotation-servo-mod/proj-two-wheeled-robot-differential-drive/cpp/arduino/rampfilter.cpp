#include <Arduino.h>

class RampFilter {
private:
    float currentVal = 0.0f;
    float maxAccel; // Максимальне прискорення (од/с)

public:
    RampFilter(float maxAcceleration) : maxAccel(maxAcceleration) {}

    float update(float targetVal, float dt) {
        float maxChange = maxAccel * dt;
        float diff = targetVal - currentVal;

        if (diff > maxChange) {
            currentVal += maxChange;
        } else if (diff < -maxChange) {
            currentVal -= maxChange;
        } else {
            currentVal = targetVal;
        }
        return currentVal;
    }

    float getCurrentValue() const { return currentVal; }
};

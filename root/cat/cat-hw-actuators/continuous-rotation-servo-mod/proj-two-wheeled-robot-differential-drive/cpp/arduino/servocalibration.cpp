#include <Arduino.h>

struct ServoCalibration {
    uint16_t tNeutral = 1500;
    uint16_t tMinFwd  = 1540;
    uint16_t tMaxFwd  = 2000;
    uint16_t tMinRev  = 1460;
    uint16_t tMaxRev  = 1000;

    uint16_t mapSpeedToPulse(float speed) const {
        speed = constrain(speed, -1.0f, 1.0f);
        if (speed > 0.0f) {
            return static_cast<uint16_t>(tMinFwd + speed * (tMaxFwd - tMinFwd));
        } else if (speed < 0.0f) {
            return static_cast<uint16_t>(tMinRev + speed * (tMinRev - tMaxRev));
        }
        return tNeutral;
    }
};

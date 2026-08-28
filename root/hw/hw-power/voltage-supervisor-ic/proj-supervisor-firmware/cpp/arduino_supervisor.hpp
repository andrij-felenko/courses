/* arduino_supervisor.hpp — C++ ООП підхід */
#pragma once
#include <Arduino.h>

class ArduinoWatchdogGuard {
public:
    ArduinoWatchdogGuard(uint8_t wdiPin, uint8_t pfoPin, uint8_t pwrPin)
        : wdiPin_(wdiPin), pfoPin_(pfoPin), pwrPin_(pwrPin) {}

    void begin() {
        pinMode(wdiPin_, OUTPUT);
        pinMode(pwrPin_, OUTPUT);
        digitalWrite(pwrPin_, HIGH);
        lastKick_ = millis();
    }

    void kickIfWindowOpen(uint32_t minMs = 45, uint32_t maxMs = 75) noexcept {
        const uint32_t elapsed = millis() - lastKick_;
        if (elapsed >= minMs && elapsed <= maxMs) {
            state_ = !state_;
            digitalWrite(wdiPin_, state_ ? HIGH : LOW);
            lastKick_ = millis();
        }
    }

private:
    uint8_t wdiPin_;
    uint8_t pfoPin_;
    uint8_t pwrPin_;
    uint32_t lastKick_{0};
    bool state_{false};
};

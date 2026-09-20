#include <Arduino.h>

class DebouncedToggle {
private:
    uint8_t pin;
    bool lastRawState;
    bool stableState;
    unsigned long lastDebounceTime;
    unsigned long debounceDelayMs;

public:
    DebouncedToggle(uint8_t inputPin, unsigned long delayMs = 20)
        : pin(inputPin), lastRawState(true), stableState(true),
          lastDebounceTime(0), debounceDelayMs(delayMs) {}

    void begin() {
        pinMode(pin, INPUT_PULLUP);
        lastRawState = digitalRead(pin);
        stableState = lastRawState;
    }

    bool update() {
        bool currentRaw = digitalRead(pin);
        unsigned long now = millis();

        if (currentRaw != lastRawState) {
            lastDebounceTime = now;
            lastRawState = currentRaw;
        }

        if ((now - lastDebounceTime) > debounceDelayMs) {
            if (currentRaw != stableState) {
                stableState = currentRaw;
                return true; // Виявлено стабільний перехід
            }
        }
        return false;
    }

    bool getState() const {
        return stableState;
    }
};

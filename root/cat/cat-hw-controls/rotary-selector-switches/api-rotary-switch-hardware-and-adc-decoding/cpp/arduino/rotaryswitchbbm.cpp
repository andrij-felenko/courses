#include <Arduino.h>

class RotarySwitchBBM {
private:
    uint8_t pins[12];
    uint8_t pinCount;
    uint8_t currentPos;
    uint8_t pendingPos;
    unsigned long lastChangeTime;
    const unsigned long debounceMs;

public:
    RotarySwitchBBM(const uint8_t* gpioPins, uint8_t count, unsigned long debounceDelay = 15)
        : pinCount(count), currentPos(0), pendingPos(0), lastChangeTime(0), debounceMs(debounceDelay) {
        for (uint8_t i = 0; i < pinCount; i++) {
            pins[i] = gpioPins[i];
            pinMode(pins[i], INPUT_PULLUP);
        }
    }

    uint8_t readPosition() {
        uint8_t rawPos = 0xFF; // BBM невизначеність
        for (uint8_t i = 0; i < pinCount; i++) {
            if (digitalRead(pins[i]) == LOW) {
                rawPos = i;
                break;
            }
        }

        if (rawPos == 0xFF || rawPos == currentPos) {
            pendingPos = currentPos;
            return currentPos;
        }

        if (rawPos != pendingPos) {
            pendingPos = rawPos;
            lastChangeTime = millis();
        } else if (millis() - lastChangeTime >= debounceMs) {
            currentPos = rawPos;
        }

        return currentPos;
    }
};

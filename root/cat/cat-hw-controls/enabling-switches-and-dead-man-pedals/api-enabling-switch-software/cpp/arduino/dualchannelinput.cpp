#include <Arduino.h>

// Клас двоканального фільтра для платформи Arduino
class DualChannelInput {
public:
    uint8_t pinA, pinB;
    bool stateA, stateB;
    bool rawA, rawB;
    unsigned long lastTimeA, lastTimeB;
    unsigned long debounceDelay;

    DualChannelInput(uint8_t pA, uint8_t pB, unsigned long delayMs = 10)
        : pinA(pA), pinB(pB), stateA(false), stateB(false),
          rawA(false), rawB(false), lastTimeA(0), lastTimeB(0), debounceDelay(delayMs) {}

    void begin() {
        pinMode(pinA, INPUT_PULLUP);
        pinMode(pinB, INPUT_PULLUP);
    }

    void update() {
        unsigned long now = millis();
        bool sampleA = !digitalRead(pinA); // Активний високий рівень
        bool sampleB = !digitalRead(pinB);

        if (sampleA != rawA) {
            rawA = sampleA;
            lastTimeA = now;
        }
        if ((now - lastTimeA) >= debounceDelay) {
            stateA = rawA;
        }

        if (sampleB != rawB) {
            rawB = sampleB;
            lastTimeB = now;
        }
        if ((now - lastTimeB) >= debounceDelay) {
            stateB = rawB;
        }
    }
};

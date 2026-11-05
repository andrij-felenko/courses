#include <Arduino.h>

class HybridGpioInput {
private:
    uint8_t pin;
    uint8_t sampleHistory;
    bool lastStableState;
    static constexpr uint8_t STABLE_SAMPLES = 4;

public:
    explicit HybridGpioInput(uint8_t pinNumber)
        : pin(pinNumber), sampleHistory(0xFF), lastStableState(false) {}

    void begin() {
        pinMode(pin, INPUT_PULLUP);
    }

    bool update() {
        // Зчитання фізичного стану піна
        bool rawState = digitalRead(pin);

        // Зсув історії та додавання нового відліку
        sampleHistory = (sampleHistory << 1) | (rawState ? 1 : 0);

        uint8_t mask = (1 << STABLE_SAMPLES) - 1;
        uint8_t pattern = sampleHistory & mask;

        if (pattern == mask) {
            lastStableState = true;
        } else if (pattern == 0x00) {
            lastStableState = false;
        }

        return lastStableState;
    }

    bool getState() const {
        return lastStableState;
    }
};

HybridGpioInput safeSensor(5);

void setup() {
    Serial.begin(115200);
    safeSensor.begin();
}

void loop() {
    bool isTriggered = safeSensor.update();
    // Використання узгодженого стану
    delay(10);
}

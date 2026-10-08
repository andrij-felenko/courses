#include <Arduino.h>

constexpr uint8_t STO_PIN_1 = 2;
constexpr uint8_t STO_PIN_2 = 3;
constexpr uint8_t GATE_ENABLE_PIN = 8;

class SafetyController {
public:
    static void IRAM_ATTR onHardwareFault() {
        // Миттєве блокування силового каскаду
        digitalWrite(GATE_ENABLE_PIN, LOW);
    }

    void begin() {
        pinMode(GATE_ENABLE_PIN, OUTPUT);
        digitalWrite(GATE_ENABLE_PIN, HIGH);

        pinMode(STO_PIN_1, INPUT_PULLUP);
        pinMode(STO_PIN_2, INPUT_PULLUP);

        attachInterrupt(digitalPinToInterrupt(STO_PIN_1), onHardwareFault, FALLING);
        attachInterrupt(digitalPinToInterrupt(STO_PIN_2), onHardwareFault, FALLING);
    }
};

SafetyController safetySys;

void setup() {
    safetySys.begin();
}

void loop() {
    // Основний цикл керування сервоприводом
}

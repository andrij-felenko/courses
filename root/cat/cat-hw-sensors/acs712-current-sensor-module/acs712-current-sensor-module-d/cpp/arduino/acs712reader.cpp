#include <Arduino.h>

class ACS712Reader {
private:
    uint8_t pin;
    float vcc;
    float sensitivity;
    uint16_t adcMax;
    uint16_t zeroOffset;

public:
    ACS712Reader(uint8_t analogPin, float supplyV = 5.0f, float sens = 0.185f, uint16_t maxAdc = 1023)
        : pin(analogPin), vcc(supplyV), sensitivity(sens), adcMax(maxAdc), zeroOffset(maxAdc / 2) {}

    void calibrateZero(uint16_t samples = 100) {
        uint32_t sum = 0;
        for (uint16_t i = 0; i < samples; i++) {
            sum += analogRead(pin);
            delay(2);
        }
        zeroOffset = sum / samples;
    }

    float getCurrentDC() const {
        uint16_t adcRaw = analogRead(pin);
        float vOut = (static_cast<float>(adcRaw) / adcMax) * vcc;
        float vZero = (static_cast<float>(zeroOffset) / adcMax) * vcc;
        return (vOut - vZero) / sensitivity;
    }
};

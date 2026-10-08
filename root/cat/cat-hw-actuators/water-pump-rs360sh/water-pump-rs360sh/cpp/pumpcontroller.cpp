#include <cstdint>

class PumpController {
private:
    uint8_t  pwmPin, adcPin;
    uint16_t dryThreshold, stallThreshold;

public:
    PumpController(uint8_t pwm, uint8_t adc, uint16_t dryTh, uint16_t stallTh)
        : pwmPin(pwm), adcPin(adc), dryThreshold(dryTh), stallThreshold(stallTh) {}

    void startAndCheck() {
        for (uint8_t duty = 60; duty <= 200; duty += 5) {
            analogWrite(pwmPin, duty);
            delay(20);
        }
        delay(300);

        uint16_t current = analogRead(adcPin);
        if (current < dryThreshold || current > stallThreshold) {
            analogWrite(pwmPin, 0);
        }
    }
};

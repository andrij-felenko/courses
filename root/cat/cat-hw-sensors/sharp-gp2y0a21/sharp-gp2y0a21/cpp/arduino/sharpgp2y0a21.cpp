#include <Arduino.h>

class SharpGP2Y0A21 {
private:
    uint8_t pin;
    float ema_state;
    const float alpha = 0.25f;

public:
    SharpGP2Y0A21(uint8_t adc_pin) : pin(adc_pin), ema_state(0.0f) {}

    void begin() {
        pinMode(pin, INPUT);
        ema_state = analogRead(pin);
    }

    float readDistanceCm() {
        uint16_t reads[5];
        for (uint8_t i = 0; i < 5; i++) {
            reads[i] = analogRead(pin);
            delayMicroseconds(150);
        }
        for (uint8_t i = 1; i < 5; i++) {
            uint16_t key = reads[i];
            int8_t j = i - 1;
            while (j >= 0 && reads[j] > key) {
                reads[j + 1] = reads[j];
                j--;
            }
            reads[j + 1] = key;
        }
        uint16_t median = reads[2];
        ema_state = (alpha * median) + ((1.0f - alpha) * ema_state);

        if (ema_state <= 20.0f) return 80.0f;
        float distance = 4800.0f / (ema_state - 20.0f);
        return constrain(distance, 10.0f, 80.0f);
    }
};

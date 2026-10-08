#include <Arduino.h>

const uint8_t ADC_PIN = A0;
const uint8_t WINDOW_SIZE = 5;

int getMedianADC(uint8_t pin) {
    int buf[WINDOW_SIZE];
    for (uint8_t i = 0; i < WINDOW_SIZE; i++) {
        buf[i] = analogRead(pin);
        delayMicroseconds(200);
    }
    for (uint8_t i = 0; i < WINDOW_SIZE - 1; i++) {
        for (uint8_t j = i + 1; j < WINDOW_SIZE; j++) {
            if (buf[i] > buf[j]) {
                int temp = buf[i];
                buf[i] = buf[j];
                buf[j] = temp;
            }
        }
    }
    return buf[WINDOW_SIZE / 2];
}

float readDistanceCM() {
    int raw = getMedianADC(ADC_PIN);
    if (raw <= 0) return -1.0f;
    float cm = 6787.0f / (static_cast<float>(raw) - 3.0f) - 4.0f;
    if (cm > 80.0f) return 80.0f;
    if (cm < 10.0f) return 10.0f;
    return cm;
}

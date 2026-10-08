/* 
 * Arduino приклад керування кроковим приводом перистальтичного дозатора. * Реалізує дозовану подачу заданого об'єму флюїду з плавною рампою швидкості. */

#include <Arduino.h>

const uint8_t STEP_PIN = 9;
const uint8_t DIR_PIN  = 8;
const uint8_t ENABLE_PIN = 7;

// Калібрування: кількість кроків драйвера на один мілілітр
const float STEPS_PER_ML = 3200.0f;

class PeristalticDoser {
public:
    void begin() {
        pinMode(STEP_PIN, OUTPUT);
        pinMode(DIR_PIN, OUTPUT);
        pinMode(ENABLE_PIN, OUTPUT);
        digitalWrite(ENABLE_PIN, HIGH); // Драйвер вимкнено
    }

    void dispense(float volumeMl, bool clockwise) {
        unsigned long totalSteps = (unsigned long)(volumeMl * STEPS_PER_ML);
        digitalWrite(DIR_PIN, clockwise ? HIGH : LOW);
        digitalWrite(ENABLE_PIN, LOW); // Увімкнути силовий каскад

        unsigned int currentDelay = 600; // Мікросекунди між кроками
        const unsigned int targetDelay = 120;
        const unsigned int accelSteps = 300;

        for (unsigned long i = 0; i < totalSteps; i++) {
            digitalWrite(STEP_PIN, HIGH);
            delayMicroseconds(3);
            digitalWrite(STEP_PIN, LOW);

            // Обчислення рампи розгону та гальмування
            if (i < accelSteps && currentDelay > targetDelay) {
                currentDelay -= 1;
            } else if (i > (totalSteps - accelSteps) && currentDelay < 600) {
                currentDelay += 1;
            }

            delayMicroseconds(currentDelay);
        }

        digitalWrite(ENABLE_PIN, HIGH); // Вимкнути силові ключі
    }
};

PeristalticDoser doser;

void setup() {
    doser.begin();
    // Видаємо 10.5 мл рідини напряму
    doser.dispense(10.5f, true);
}

void loop() {
    // Очікування нових команд
}

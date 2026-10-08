// Програмна компенсація провалу тиску перистальтичної помпи на Arduino
#include <Arduino.h>

const uint8_t STEP_PIN = 9;
const uint8_t DIR_PIN = 8;
const uint16_t STEPS_PER_REV = 200;
const uint8_t ROLLERS_COUNT = 3;

// Кількість кроків між моментами відриву роликів
const uint16_t STEPS_PER_ROLLER = STEPS_PER_REV / ROLLERS_COUNT;

void stepPump(uint16_t currentStep) {
    uint16_t phase = currentStep % STEPS_PER_ROLLER;
    uint16_t stepDelayUs = 1000; // Базовий інтервал між кроками (1 мс)

    // При наближенні до зони відриву ролика (останні 10% кроків фази)
    // короткочасно прискорюємо привід для компенсації backflow
    if (phase > (STEPS_PER_ROLLER * 9 / 10)) {
        stepDelayUs = 400; // Прискорення зменшує провал тиску
    }

    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(stepDelayUs);
}

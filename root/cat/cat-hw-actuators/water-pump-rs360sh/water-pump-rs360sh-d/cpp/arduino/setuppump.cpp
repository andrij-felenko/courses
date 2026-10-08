#include <Arduino.h>

const int PUMP_PWM_PIN = 9;
const int PWM_FREQUENCY = 15000; // Частота 15 кГц

void setupPump() {
    pinMode(PUMP_PWM_PIN, OUTPUT);
    analogWrite(PUMP_PWM_PIN, 0);
}

void setPumpFlowSmooth(uint8_t targetDuty, unsigned long rampTimeMs) {
    static uint8_t currentDuty = 0;
    if (targetDuty == currentDuty) return;
    
    int steps = abs((int)targetDuty - (int)currentDuty);
    if (steps == 0) return;
    
    unsigned long stepDelay = rampTimeMs / steps;
    int stepDir = (targetDuty > currentDuty) ? 1 : -1;
    
    while (currentDuty != targetDuty) {
        currentDuty += stepDir;
        analogWrite(PUMP_PWM_PIN, currentDuty);
        delay(stepDelay);
    }
}

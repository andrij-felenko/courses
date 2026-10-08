// Обчислення тривалості імпульсу ШІМ та перевірка зони нечутливості
#include <Arduino.h>

const uint16_t PULSE_MIN_US = 1000;
const uint16_t PULSE_MAX_US = 2000;
const float ANGLE_MAX_DEG = 180.0f;
const uint16_t DEADBAND_US = 5;

uint16_t angleToPulseUs(float angleDeg) {
    if (angleDeg < 0.0f) angleDeg = 0.0f;
    if (angleDeg > ANGLE_MAX_DEG) angleDeg = ANGLE_MAX_DEG;
    
    float pulse = PULSE_MIN_US + (angleDeg / ANGLE_MAX_DEG) * (PULSE_MAX_US - PULSE_MIN_US);
    return (uint16_t)(pulse + 0.5f);
}

bool isTargetOutsideDeadband(uint16_t currentPulseUs, uint16_t targetPulseUs) {
    int16_t diff = (int16_t)targetPulseUs - (int16_t)currentPulseUs;
    return (abs(diff) > DEADBAND_US);
}

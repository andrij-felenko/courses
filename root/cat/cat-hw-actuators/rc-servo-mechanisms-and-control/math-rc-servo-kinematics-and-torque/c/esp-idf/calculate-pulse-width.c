// Обчислення тривалості імпульсу для генерації ШІМ в ESP-IDF
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define SERVO_MIN_PULSE_US 1000
#define SERVO_MAX_PULSE_US 2000
#define SERVO_MAX_ANGLE    180.0f
#define SERVO_DEADBAND_US  5

uint32_t calculate_pulse_width(float target_angle) {
    if (target_angle < 0.0f) target_angle = 0.0f;
    if (target_angle > SERVO_MAX_ANGLE) target_angle = SERVO_MAX_ANGLE;
    
    float pulse = SERVO_MIN_PULSE_US + (target_angle / SERVO_MAX_ANGLE) * 
                  (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US);
    return (uint32_t)lroundf(pulse);
}

bool check_deadband_threshold(uint32_t current_pulse, uint32_t target_pulse) {
    int32_t delta = (int32_t)target_pulse - (int32_t)current_pulse;
    return (labs(delta) > SERVO_DEADBAND_US);
}

#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint16_t deadband_adc;    // Ширина зони нечутливості в відліках АЦП
    uint16_t kp_num;          // Чисельник коефіцієнта підсилення K_p
    uint16_t kp_den;          // Знаменник коефіцієнта підсилення K_p
    uint16_t last_filtered;   // Останнє відфільтроване значення позиції
} ServoControllerC;

// Експоненційне згладжування шумів АЦП та обчислення керування
int16_t Servo_ComputeOutput(ServoControllerC *ctrl, uint16_t raw_adc, uint16_t setpoint_adc) {
    // 1. Фільтрація високочастотного шуму потенціометра (EMA-фільтр: alpha = 0.25)
    ctrl->last_filtered = (uint16_t)(((uint32_t)raw_adc + 3 * (uint32_t)ctrl->last_filtered) / 4);
    
    // 2. Обчислення похибки позиціонування
    int32_t error = (int32_t)setpoint_adc - (int32_t)ctrl->last_filtered;
    
    // 3. Перевірка зони нечутливості (deadband)
    if (abs(error) <= (int32_t)ctrl->deadband_adc) {
        return 0; // Мотор вимкнено в межах зони нечутливості
    }
    
    // 4. Коррегування похибки на величину deadband для плавності старту
    if (error > 0) {
        error -= ctrl->deadband_adc;
    } else {
        error += ctrl->deadband_adc;
    }
    
    // 5. Обчислення пропорційного управляючого сигналу H-моста
    int32_t output = (error * ctrl->kp_num) / ctrl->kp_den;
    
    // Обмеження виходу (PWM limit ±1000)
    if (output > 1000) output = 1000;
    if (output < -1000) output = -1000;
    
    return (int16_t)output;
}

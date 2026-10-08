#include <stdint.h>
#include <stdlib.h>

// Структура конфігурації та стану контуру позиціонування
typedef struct {
    int16_t target_adc;   // Заданий код АЦП (setpoint)
    int16_t deadband;     // Напівширина зони нечутливості у LSB
    float kp;             // Пропорційний коефіцієнт
    int16_t max_pwm;      // Максимальне значення ШІМ (наприклад, 255)
} servo_loop_t;

// Обчислення вихідного сигналу ШІМ (-max_pwm ... +max_pwm)
int16_t servo_loop_calculate(const servo_loop_t *loop, int16_t current_adc) {
    // 1. Обчислення сирого сигналу помилки
    int16_t error = loop->target_adc - current_adc;
    
    // 2. Застосування зони нечутливості (deadband)
    int16_t effective_error = 0;
    if (abs(error) > loop->deadband) {
        if (error > 0) {
            effective_error = error - loop->deadband;
        } else {
            effective_error = error + loop->deadband;
        }
    } else {
        // Усередині зони нечутливості сигнал помилки строго нульовий
        return 0;
    }
    
    // 3. Пропорційне регулювання
    float raw_pwm = loop->kp * (float)effective_error;
    
    // 4. Обмеження насичення (clamping)
    if (raw_pwm > (float)loop->max_pwm) {
        return loop->max_pwm;
    } else if (raw_pwm < -(float)loop->max_pwm) {
        return -loop->max_pwm;
    }
    
    return (int16_t)raw_pwm;
}

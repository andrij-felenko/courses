#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float kp;
    float ki;
    float kd;
    float prev_error;
    float integral;
} pid_controller_t;

uint16_t calculate_pwm_duty(pid_controller_t *pid, float setpoint, float current_temp, float dt, float v_src, float p_max, float r_tip) {
    float error = setpoint - current_temp;
    pid->integral += error * dt;
    float derivative = (error - pid->prev_error) / dt;
    pid->prev_error = error;

    float output = (pid->kp * error) + (pid->ki * pid->integral) + (pid->kd * derivative);

    // Розрахунок пікової потужності та максимального коефіцієнта заповнення
    float p_peak = (v_src * v_src) / r_tip;
    float max_duty = p_max / p_peak;
    if (max_duty > 1.0f) {
        max_duty = 1.0f;
    }

    // Обмеження вихідного сигналу регулятора
    if (output > max_duty) {
        output = max_duty;
    } else if (output < 0.0f) {
        output = 0.0f;
    }

    // Переведення в значення 12-бітного регістра ШІМ (0..4095)
    return (uint16_t)(output * 4095.0f);
}

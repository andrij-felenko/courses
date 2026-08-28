/* Драйвер сервомеханічного захвату маніпулятора (C99 / FreeRTOS) */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    GRIPPER_STATE_IDLE = 0,
    GRIPPER_STATE_CLOSING,
    GRIPPER_STATE_HOLDING,
    GRIPPER_STATE_OPENING,
    GRIPPER_STATE_FAULT
} gripper_state_t;

typedef enum {
    GRIPPER_ERR_NONE = 0,
    GRIPPER_ERR_TIMEOUT,
    GRIPPER_ERR_OVERCURRENT,
    GRIPPER_ERR_SLIP_DETECTED
} gripper_error_t;

typedef struct {
    /* Калібрувальні коефіцієнти приводу */
    float current_to_force_nm;   /* Коефіцієнт: Ньютони сили на Ампер струму (Н/А) */
    float contact_current_a;     /* Поріг струму для виявлення торкання (А) */
    float max_allowed_current_a; /* Струмовий захист приводу (А) */
    float kp_force;              /* Пропорційний коефіцієнт регулятора сили */
    float ki_force;              /* Інтегральний коефіцієнт регулятора сили */

    /* Поточний стан */
    gripper_state_t state;
    gripper_error_t error;
    float target_force_n;
    float measured_current_a;
    float measured_position_mm;
    float force_integral;
    uint32_t state_timer_ms;
} gripper_controller_t;

/* Ініціалізація структури контролера */
void gripper_init(gripper_controller_t *ctrl, float force_gain, float contact_current) {
    ctrl->current_to_force_nm = force_gain;
    ctrl->contact_current_a = contact_current;
    ctrl->max_allowed_current_a = 4.5f;
    ctrl->kp_force = 0.05f;
    ctrl->ki_force = 0.002f;
    ctrl->state = GRIPPER_STATE_IDLE;
    ctrl->error = GRIPPER_ERR_NONE;
    ctrl->target_force_n = 0.0f;
    ctrl->force_integral = 0.0f;
    ctrl->state_timer_ms = 0;
}

/* Команда на затискання із заданою силою */
void gripper_grip(gripper_controller_t *ctrl, float target_force_n) {
    ctrl->target_force_n = target_force_n;
    ctrl->force_integral = 0.0f;
    ctrl->state = GRIPPER_STATE_CLOSING;
    ctrl->error = GRIPPER_ERR_NONE;
    ctrl->state_timer_ms = 0;
}

/* Періодичний крок керування (виклик у контурі 100–500 Гц) */
float gripper_update(gripper_controller_t *ctrl, float current_a, float pos_mm, uint32_t dt_ms) {
    ctrl->measured_current_a = current_a;
    ctrl->measured_position_mm = pos_mm;
    ctrl->state_timer_ms += dt_ms;

    /* Захист від критичного перевантаження по струму */
    if (fabsf(current_a) > ctrl->max_allowed_current_a) {
        ctrl->state = GRIPPER_STATE_FAULT;
        ctrl->error = GRIPPER_ERR_OVERCURRENT;
        return 0.0f;
    }

    float output_pwm = 0.0f;

    switch (ctrl->state) {
        case GRIPPER_STATE_IDLE:
            output_pwm = 0.0f;
            break;

        case GRIPPER_STATE_CLOSING:
            /* Рух на закривання з постійною базовою швидкістю */
            output_pwm = 0.35f;

            /* Детектування моменту контакту з об'єктом за стрибком струму */
            if (current_a > ctrl->contact_current_a) {
                ctrl->state = GRIPPER_STATE_HOLDING;
                ctrl->force_integral = 0.0f;
            }

            /* Захист по таймауту повного закривання */
            if (ctrl->state_timer_ms > 3000) {
                ctrl->state = GRIPPER_STATE_FAULT;
                ctrl->error = GRIPPER_ERR_TIMEOUT;
                output_pwm = 0.0f;
                break;
            }
            break;

        case GRIPPER_STATE_HOLDING: {
            /* Поточна оцінена нормальна сила стискання */
            float estimated_force = current_a * ctrl->current_to_force_nm;
            float force_error = ctrl->target_force_n - estimated_force;

            /* PI регулятор сили стискання */
            ctrl->force_integral += force_error * (float)dt_ms;
            
            /* Анти-віндап обмеження інтегратора */
            if (ctrl->force_integral > 100.0f) ctrl->force_integral = 100.0f;
            if (ctrl->force_integral < -100.0f) ctrl->force_integral = -100.0f;

            output_pwm = (ctrl->kp_force * force_error) + (ctrl->ki_force * ctrl->force_integral);

            /* Гарантований базовий струм утримання */
            if (output_pwm < 0.15f) output_pwm = 0.15f;
            if (output_pwm > 0.90f) output_pwm = 0.90f;

            /* Виявлення раптової втрати/вислизання вантажу */
            if (current_a < (ctrl->contact_current_a * 0.4f) && ctrl->state_timer_ms > 500) {
                ctrl->state = GRIPPER_STATE_FAULT;
                ctrl->error = GRIPPER_ERR_SLIP_DETECTED;
                output_pwm = 0.0f;
            }
            break;
        }

        case GRIPPER_STATE_OPENING:
            output_pwm = -0.50f; /* Зворотний хід */
            if (pos_mm <= 1.0f || ctrl->state_timer_ms > 2000) {
                ctrl->state = GRIPPER_STATE_IDLE;
                output_pwm = 0.0f;
            }
            break;

        case GRIPPER_STATE_FAULT:
        default:
            output_pwm = 0.0f;
            break;
    }

    return output_pwm;
}

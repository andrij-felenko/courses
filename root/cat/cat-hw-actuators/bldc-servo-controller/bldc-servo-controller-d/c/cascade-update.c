#include <math.h>

typedef struct {
    float kp_pos;
    float kp_vel;
    float ki_vel;
    float vel_integrator;
    float max_vel;
    float max_current;
} CascadeController;

// Обчислення одного кроку каскадного регулятора (позиція -> швидкість -> струм I_q)
float cascade_update(CascadeController *ctrl, float target_pos, float current_pos, float current_vel, float dt) {
    // 1. Зовнішній контур позиції (P-регулятор)
    float pos_error = target_pos - current_pos;
    float target_vel = pos_error * ctrl->kp_pos;

    // Обмеження максимальної швидкості
    if (target_vel > ctrl->max_vel) target_vel = ctrl->max_vel;
    if (target_vel < -ctrl->max_vel) target_vel = -ctrl->max_vel;

    // 2. Проміжний контур швидкості (ПІ-регулятор)
    float vel_error = target_vel - current_vel;
    ctrl->vel_integrator += vel_error * ctrl->ki_vel * dt;

    // Anti-windup: обмеження інтегратора струму
    if (ctrl->vel_integrator > ctrl->max_current) ctrl->vel_integrator = ctrl->max_current;
    if (ctrl->vel_integrator < -ctrl->max_current) ctrl->vel_integrator = -ctrl->max_current;

    float i_q_target = vel_error * ctrl->kp_vel + ctrl->vel_integrator;

    // Обмеження максимального струму I_q
    if (i_q_target > ctrl->max_current) i_q_target = ctrl->max_current;
    if (i_q_target < -ctrl->max_current) i_q_target = -ctrl->max_current;

    return i_q_target;
}

#include <math.h>

typedef struct {
    float Kp;
    float Ki_d;     /* Ki * Ts */
    float Kbc;      /* Коефіцієнт back-calculation */
    float out_min;
    float out_max;
    float integrator;
} PIController;

/* Ініціалізація ПІ-регулятора */
void PI_Init(PIController *pi, float Kp, float Ki, float Ts, float Kbc, float min, float max) {
    pi->Kp = Kp;
    pi->Ki_d = Ki * Ts;
    pi->Kbc = Kbc;
    pi->out_min = min;
    pi->out_max = max;
    pi->integrator = 0.0f;
}

/* Обчислення ПІ-кроку з anti-windup (Back-Calculation) */
float PI_Update(PIController *pi, float setpoint, float feedback) {
    float error = setpoint - feedback;
    float p_term = pi->Kp * error;
    float u_unsat = p_term + pi->integrator;

    /* Обмеження виходу (насичення) */
    float u_sat = u_unsat;
    if (u_sat > pi->out_max) {
        u_sat = pi->out_max;
    } else if (u_sat < pi->out_min) {
        u_sat = pi->out_min;
    }

    /* Зворотне обчислення для інтегратора */
    float error_sat = u_sat - u_unsat;
    pi->integrator += pi->Ki_d * error + pi->Kbc * error_sat;

    return u_sat;
}

/* Цифровий ПІД-регулятор із контуром зворотного перерахунку Back-Calculation (C99) */

#include <stdbool.h>

typedef struct {
    float kp;               /* Коефіцієнт підсилення пропорційної ланки */
    float ti;               /* Стала часу інтегрування (секунди) */
    float td;               /* Стала часу диференціювання (секунди) */
    float tt;               /* Стала часу стеження anti-windup (секунди) */
    float nd;               /* Коефіцієнт фільтра D-члена (типово 10.0) */
    float ts;               /* Період дискретизації переривання (секунди) */
    float u_min;            /* Нижня фізична межа насичення */
    float u_max;            /* Верхня фізична межа насичення */

    float integrator_state; /* Поточний накопичений стан інтегратора */
    float filter_d_state;   /* Поточний стан аперіодичного фільтра D-члена */
    float prev_pv;          /* Значення датчика на попередньому такті */
    float prev_u_unsat;     /* Ненасичений сигнал попереднього такту */
    float prev_u_sat;       /* Обмежений сигнал попереднього такту */
} pid_controller_t;

void pid_init(pid_controller_t *pid, float kp, float ti, float td, float ts,
              float u_min, float u_max) {
    pid->kp = kp;
    pid->ti = (ti > 0.0f) ? ti : 1e-3f;
    pid->td = (td >= 0.0f) ? td : 0.0f;
    pid->tt = pid->ti;      /* За правилом Острема для ПІ: Tt = Ti */
    pid->nd = 10.0f;
    pid->ts = ts;
    pid->u_min = u_min;
    pid->u_max = u_max;

    pid->integrator_state = 0.0f;
    pid->filter_d_state = 0.0f;
    pid->prev_pv = 0.0f;
    pid->prev_u_unsat = 0.0f;
    pid->prev_u_sat = 0.0f;
}

float pid_step(pid_controller_t *pid, float setpoint, float process_val) {
    float error = setpoint - process_val;

    /* 1. Пропорційний канал */
    float p_term = pid->kp * error;

    /* 2. Диференціальний канал за вимірюванням із фільтром низьких частот */
    float d_term = 0.0f;
    if (pid->td > 0.0f) {
        float denom = pid->td + pid->nd * pid->ts;
        float alpha = pid->td / denom;
        float beta  = (pid->kp * pid->td * pid->nd) / denom;
        float delta_pv = process_val - pid->prev_pv;

        pid->filter_d_state = alpha * pid->filter_d_state - beta * delta_pv;
        d_term = pid->filter_d_state;
    }

    /* 3. Інтегральний канал із розвантаженням Back-Calculation */
    float tracking_error = pid->prev_u_sat - pid->prev_u_unsat;
    float tracking_corr  = (pid->ts / pid->tt) * tracking_error;
    float ki_step        = (pid->kp / pid->ti) * pid->ts * error;

    pid->integrator_state += ki_step + tracking_corr;

    /* 4. Повний розрахунковий вихід */
    float u_unsat = p_term + pid->integrator_state + d_term;

    /* 5. Оператор фізичного насичення sat(u) */
    float u_sat = u_unsat;
    if (u_sat > pid->u_max) u_sat = pid->u_max;
    if (u_sat < pid->u_min) u_sat = pid->u_min;

    /* Збереження стану для наступного кроку */
    pid->prev_pv = process_val;
    pid->prev_u_unsat = u_unsat;
    pid->prev_u_sat = u_sat;

    return u_sat;
}

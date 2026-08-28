/* Промисловий цифровий ПІД-регулятор з Anti-Windup (C99 / C11) */

#include <stdbool.h>
#include <stddef.h>
#include <math.h>

typedef enum {
    PID_ANTI_WINDUP_NONE = 0,
    PID_ANTI_WINDUP_CLAMPING,
    PID_ANTI_WINDUP_BACK_CALCULATION
} pid_anti_windup_mode_t;

typedef struct {
    /* Параметри налаштування регулятора */
    float kp;               /* Пропорційний коефіцієнт підсилення */
    float ti;               /* Стала часу інтегрування (с) */
    float td;               /* Стала часу диференціювання (с) */
    float tt;               /* Стала часу стеження anti-windup (с) */
    float nd;               /* Коефіцієнт фільтрації D-члена (типово 10.0) */
    float beta;             /* Ваговий коефіцієнт уставки для P-члена (0.0..1.0) */
    float ts;               /* Період дискретизації квантування (с) */
    float out_min;          /* Нижня фізична межа насичення виходу */
    float out_max;          /* Верхня фізична межа насичення виходу */
    pid_anti_windup_mode_t aw_mode; /* Обраний режим захисту від windup */

    /* Внутрішні змінні стану */
    float integrator_state; /* Накопичений стан інтегратора */
    float deriv_filter_state; /* Стан аперіодичного фільтра D-члена */
    float prev_pv;          /* Значення вимірюваної величини на попередньому кроці */
    float prev_unsat_out;   /* Повний ненасичений вихід на попередньому кроці */
    float prev_sat_out;     /* Реальний обмежений вихід на попередньому кроці */
    bool is_manual;         /* Прапорець ручного режиму керування */
} pid_controller_t;

void pid_init(pid_controller_t *pid, float kp, float ti, float td, float ts,
              float out_min, float out_max, pid_anti_windup_mode_t aw_mode) {
    if (!pid || ts <= 0.0f) return;

    pid->kp = kp;
    pid->ti = (ti > 0.0f) ? ti : 1e-3f;
    pid->td = (td >= 0.0f) ? td : 0.0f;
    pid->tt = (ti > 0.0f) ? ti : 1e-3f; /* За замовчуванням Tt = Ti */
    pid->nd = 10.0f;
    pid->beta = 1.0f;
    pid->ts = ts;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->aw_mode = aw_mode;

    pid->integrator_state = 0.0f;
    pid->deriv_filter_state = 0.0f;
    pid->prev_pv = 0.0f;
    pid->prev_unsat_out = 0.0f;
    pid->prev_sat_out = 0.0f;
    pid->is_manual = false;
}

void pid_reset(pid_controller_t *pid, float current_pv) {
    if (!pid) return;
    pid->integrator_state = 0.0f;
    pid->deriv_filter_state = 0.0f;
    pid->prev_pv = current_pv;
    pid->prev_unsat_out = 0.0f;
    pid->prev_sat_out = 0.0f;
}

void pid_set_manual_output(pid_controller_t *pid, float manual_out, float current_pv) {
    if (!pid) return;
    pid->is_manual = true;
    pid->prev_pv = current_pv;

    /* Обмеження сигналу за фізичними межами */
    if (manual_out > pid->out_max) manual_out = pid->out_max;
    if (manual_out < pid->out_min) manual_out = pid->out_min;

    pid->prev_sat_out = manual_out;
    pid->prev_unsat_out = manual_out;

    /* Підгонка інтегратора для безударного переходу (Bumpless Transfer) */
    float p_term = pid->kp * (pid->beta * current_pv - current_pv);
    pid->integrator_state = manual_out - p_term;
}

void pid_set_auto_mode(pid_controller_t *pid) {
    if (!pid) return;
    pid->is_manual = false;
}

float pid_update(pid_controller_t *pid, float sp, float pv) {
    if (!pid) return 0.0f;

    /* У ручному режимі вихід жорстко зафіксовано оператором */
    if (pid->is_manual) {
        return pid->prev_sat_out;
    }

    float error = sp - pv;

    /* 1. Пропорційний канал із вагою уставки beta */
    float p_term = pid->kp * (pid->beta * sp - pv);

    /* 2. Диференціювання за вимірюванням з аперіодичним фільтром */
    float d_term = 0.0f;
    if (pid->td > 0.0f) {
        float denom = pid->td + pid->nd * pid->ts;
        float alpha = pid->td / denom;
        float beta_d = (pid->kp * pid->td * pid->nd) / denom;
        float delta_pv = pv - pid->prev_pv;

        pid->deriv_filter_state = alpha * pid->deriv_filter_state - beta_d * delta_pv;
        d_term = pid->deriv_filter_state;
    }

    /* 3. Оновлення стану інтегратора залежно від алгоритму Anti-Windup */
    float ki_gain = (pid->kp / pid->ti) * pid->ts;

    switch (pid->aw_mode) {
        case PID_ANTI_WINDUP_CLAMPING: {
            bool saturated_high = (pid->prev_unsat_out >= pid->out_max);
            bool saturated_low  = (pid->prev_unsat_out <= pid->out_min);
            bool error_positive = (error > 0.0f);
            bool error_negative = (error < 0.0f);

            /* Заморожуємо інтегрування, якщо насичено і похибка діє на поглиблення насичення */
            bool clamp = (saturated_high && error_positive) || (saturated_low && error_negative);
            if (!clamp) {
                pid->integrator_state += ki_gain * error;
            }
            break;
        }

        case PID_ANTI_WINDUP_BACK_CALCULATION: {
            float tracking_error = pid->prev_sat_out - pid->prev_unsat_out;
            float tracking_correction = (pid->ts / pid->tt) * tracking_error;
            pid->integrator_state += ki_gain * error + tracking_correction;
            break;
        }

        case PID_ANTI_WINDUP_NONE:
        default:
            pid->integrator_state += ki_gain * error;
            break;
    }

    /* 4. Формування повного розрахункового сигналу */
    float unsat_out = p_term + pid->integrator_state + d_term;

    /* 5. Фізичне насичення виконавчого органу sat(u) */
    float sat_out = unsat_out;
    if (sat_out > pid->out_max) sat_out = pid->out_max;
    if (sat_out < pid->out_min) sat_out = pid->out_min;

    /* Збереження стану для наступного циклу */
    pid->prev_pv = pv;
    pid->prev_unsat_out = unsat_out;
    pid->prev_sat_out = sat_out;

    return sat_out;
}

/* ============================================================================
 * digital_avr.h / digital_avr.c — Цифровий регулятор напруги генератора (C99)
 * ============================================================================ */
#ifndef DIGITAL_AVR_H
#define DIGITAL_AVR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float kp;               /* Пропорційний коефіцієнт регулятора */
    float ki;               /* Інтегральний коефіцієнт регулятора */
    float kd;               /* Диференціальний коефіцієнт регулятора */
    float i_term;           /* Накопичена інтегральна сума */
    float prev_error;       /* Попередня похибка для розрахунку D-складової */
    float duty_min;         /* Мінімальна шпаруватість ШІМ (0.0) */
    float duty_max;         /* Максимальна шпаруватість ШІМ (1.0) */
    float v_target_base;    /* Базова цільова напруга при 25°C (14.4 В) */
    float temp_coeff;       /* Температурний коефіцієнт (-0.015 В/°C) */
    float v_filt;           /* Відфільтрована вихідна напруга генератора */
    float prev_v_raw;       /* Попереднє сире значення напруги для dV/dt */
    float current_duty;     /* Поточна фактична шпаруватість ШІМ ротора */
    float lrc_slew_rate;    /* Максимальна швидкість наростання ШІМ (1/с) */
    bool  load_dump_active; /* Прапорець аварійного режиму Load Dump */
} avr_controller_t;

void avr_init(avr_controller_t *avr, float v_base, float kp, float ki, float kd);
float avr_update(avr_controller_t *avr, float v_raw, float temp_c, float dt);
void avr_reset_faults(avr_controller_t *avr);

#ifdef __cplusplus
}
#endif

#endif /* DIGITAL_AVR_H */

/* ── Реалізація digital_avr.c ──────────────────────────────────────────────── */
#include <math.h>

#define IIR_ALPHA           0.125f   /* Коефіцієнт згладжування IIR фільтра */
#define LOAD_DUMP_VOLTAGE   16.50f   /* Поріг відключення при Load Dump (В) */
#define LOAD_DUMP_SLOPE     50.0f    /* Поріг швидкості наростання (В/мс) */

void avr_init(avr_controller_t *avr, float v_base, float kp, float ki, float kd)
{
    if (!avr) return;
    avr->kp = kp;
    avr->ki = ki;
    avr->kd = kd;
    avr->i_term = 0.0f;
    avr->prev_error = 0.0f;
    avr->duty_min = 0.0f;
    avr->duty_max = 1.0f;
    avr->v_target_base = v_base;
    avr->temp_coeff = -0.015f;
    avr->v_filt = v_base;
    avr->prev_v_raw = v_base;
    avr->current_duty = 0.0f;
    avr->lrc_slew_rate = 0.25f;      /* 25% шпаруватості за 1 секунду */
    avr->load_dump_active = false;
}

float avr_update(avr_controller_t *avr, float v_raw, float temp_c, float dt)
{
    if (!avr || dt <= 0.0f) return 0.0f;

    /* 1. Фільтрація вихідної напруги від високочастотних пульсацій */
    avr->v_filt += IIR_ALPHA * (v_raw - avr->v_filt);

    /* 2. Детектування аварійного скидання навантаження (Load Dump) */
    float dv_dt = (v_raw - avr->prev_v_raw) / (dt * 1000.0f);
    avr->prev_v_raw = v_raw;

    if (v_raw >= LOAD_DUMP_VOLTAGE || dv_dt >= LOAD_DUMP_SLOPE) {
        avr->load_dump_active = true;
        avr->current_duty = 0.0f;
        avr->i_term = 0.0f;
        return 0.0f;
    }

    if (avr->load_dump_active) {
        /* Чекаємо повного повернення напруги в безпечний робочий діапазон */
        if (v_raw <= avr->v_target_base) {
            avr->load_dump_active = false;
        } else {
            return 0.0f;
        }
    }

    /* 3. Термокомпенсація цільової уставки напруги */
    float v_target = avr->v_target_base + avr->temp_coeff * (temp_c - 25.0f);
    if (v_target < 13.2f) v_target = 13.2f;
    if (v_target > 15.2f) v_target = 15.2f;

    /* 4. Обчислення похибки регулювання */
    float error = v_target - avr->v_filt;

    /* 5. Пропорційна та диференціальна складові */
    float p_term = avr->kp * error;
    float d_term = avr->kd * (error - avr->prev_error) / dt;
    avr->prev_error = error;

    /* 6. Інтегрування з захистом від насичення (Anti-Windup) */
    float tentative_duty = p_term + avr->i_term + (avr->ki * error * dt) + d_term;
    if (tentative_duty >= avr->duty_min && tentative_duty <= avr->duty_max) {
        avr->i_term += avr->ki * error * dt;
    }

    float calculated_duty = p_term + avr->i_term + d_term;
    if (calculated_duty > avr->duty_max) calculated_duty = avr->duty_max;
    if (calculated_duty < avr->duty_min) calculated_duty = avr->duty_min;

    /* 7. Контроль відгуку навантаження (LRC Slew-Rate Limiter) */
    float max_step = avr->lrc_slew_rate * dt;
    if (calculated_duty > avr->current_duty + max_step) {
        avr->current_duty += max_step;
    } else {
        avr->current_duty = calculated_duty;
    }

    return avr->current_duty;
}

void avr_reset_faults(avr_controller_t *avr)
{
    if (avr) {
        avr->load_dump_active = false;
        avr->i_term = 0.0f;
    }
}

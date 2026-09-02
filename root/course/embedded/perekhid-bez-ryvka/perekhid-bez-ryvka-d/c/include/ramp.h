#ifndef RAMP_H
#define RAMP_H

#include <stdbool.h>

/* Генератори траєкторій: усе, що стоїть МІЖ ціллю місії та входом контуру. */

/* Метод 1: обмежувач швидкості наростання. max_step = rate_max * dt;
   max_step <= 0 означає «ремпінг вимкнено» — уставка стрибає одразу. */
float ramp_slew_step(float current, float target, float max_step);

/* Метод 2: фільтр нижніх частот першого порядку, alpha = dt / (dt + tau). */
float ramp_lpf_step(float current, float target, float dt, float tau);

/* Метод 3: мінімально-ривковий поліном 5-го порядку
       s(x) = 10x^3 - 15x^4 + 6x^5,  x = t / T,
   у якого обмежені всі три похідні:
       max|s'|   = 1.875 * D / T
       max|s''|  = 10/sqrt(3) * D / T^2
       max|s'''| = 60 * D / T^3
   Тривалість T беремо найбільшу з трьох, щоб жодна межа не порушилась. */
typedef struct {
    float start;
    float delta;
    float duration;
    float t;
    float position;
    float velocity;
    float acceleration;
    bool  active;
} scurve_t;

void scurve_start(scurve_t *s, float start, float goal,
                  float v_max, float a_max, float j_max);

/* Повертає true, поки профіль триває. */
bool scurve_step(scurve_t *s, float dt);

#endif /* RAMP_H */

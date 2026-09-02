/*
 * Числові дрібниці контуру. Усе inline: на Cortex-M кожна з цих
 * функцій розгортається в одну-дві інструкції FPU.
 */
#ifndef PID_NUM_H
#define PID_NUM_H

#include <math.h>
#include <stdbool.h>

/*
 * Затиск у межі. Порядок порівнянь важливий: NaN не більший і не менший
 * за жодне число, тож він пройшов би наскрізь — саме тому в регуляторі
 * скінченність перевіряють ДО затиску, а не після.
 */
static inline float pid_clampf(float value, float lo, float hi) {
    if (value < lo) {
        return lo;
    }
    if (value > hi) {
        return hi;
    }
    return value;
}

static inline bool pid_is_finite(float value) {
    return isfinite(value) != 0;
}

/*
 * Крок обмежувача темпу уставки.
 *
 * `rate` <= 0 вимикає ремпінг: уставка стрибає в ціль одразу.
 * `limited` каже, чи крок справді впирався в обмеження, — це йде
 * в телеметрію прапорцем PID_FLAG_SLEWING.
 */
static inline float pid_slew_step(float current, float target,
                                  float rate, float dt, bool *limited) {
    float max_step;
    float delta;

    *limited = false;
    if (!pid_is_finite(target)) {
        /* Уставку зіпсували ззовні — тримаємо те, що є. */
        return current;
    }
    if (!(rate > 0.0f)) {
        return target;
    }

    max_step = rate * dt;
    delta = target - current;
    if (delta > max_step) {
        *limited = true;
        return current + max_step;
    }
    if (delta < -max_step) {
        *limited = true;
        return current - max_step;
    }
    return target;
}

#endif /* PID_NUM_H */

#include "ramp.h"

#include <math.h>

float ramp_slew_step(float current, float target, float max_step)
{
    if (!(max_step > 0.0f)) {
        return target; /* ремпінг вимкнено: уставка стрибає одразу */
    }

    const float delta = target - current;
    if (delta > max_step) {
        return current + max_step;
    }
    if (delta < -max_step) {
        return current - max_step;
    }
    return target;
}

float ramp_lpf_step(float current, float target, float dt, float tau)
{
    if (!(tau > 0.0f) || !(dt > 0.0f)) {
        return target;
    }

    const float alpha = dt / (dt + tau);
    return current + alpha * (target - current);
}

void scurve_start(scurve_t *s, float start, float goal,
                  float v_max, float a_max, float j_max)
{
    s->start = start;
    s->delta = goal - start;
    s->t = 0.0f;
    s->position = start;
    s->velocity = 0.0f;
    s->acceleration = 0.0f;

    const float distance = fabsf(s->delta);
    if (distance < 1e-6f || !(v_max > 0.0f) || !(a_max > 0.0f) || !(j_max > 0.0f)) {
        /* Рухатися нікуди або межі задані безглуздо — профілю немає. */
        s->duration = 0.0f;
        s->position = goal;
        s->active = false;
        return;
    }

    /* Кожна межа диктує свою мінімальну тривалість; беремо найдовшу. */
    const float t_vel = 1.875f * distance / v_max;
    const float t_acc = sqrtf(5.7735f * distance / a_max);
    const float t_jerk = cbrtf(60.0f * distance / j_max);

    float duration = t_vel;
    if (t_acc > duration) duration = t_acc;
    if (t_jerk > duration) duration = t_jerk;

    s->duration = duration;
    s->active = true;
}

bool scurve_step(scurve_t *s, float dt)
{
    if (!s->active) {
        return false;
    }

    s->t += dt;
    float x = s->t / s->duration;
    if (x >= 1.0f) {
        x = 1.0f;
        s->active = false;
    }

    const float x2 = x * x;
    const float x3 = x2 * x;
    const float x4 = x3 * x;
    const float x5 = x4 * x;

    s->position = s->start + s->delta * (10.0f * x3 - 15.0f * x4 + 6.0f * x5);
    s->velocity = s->delta * (30.0f * x2 - 60.0f * x3 + 30.0f * x4) / s->duration;
    s->acceleration = s->delta * (60.0f * x - 180.0f * x2 + 120.0f * x3)
                      / (s->duration * s->duration);

    if (!s->active) {
        /* На кінці профілю всі похідні мінімально-ривкового полінома нульові;
           дочищаємо їх від похибки заокруглення. */
        s->velocity = 0.0f;
        s->acceleration = 0.0f;
    }
    return s->active;
}

#include "throttle.h"

#include <math.h>

float fm_throttle_mismatch(const fm_state_t *s)
{
    if (!s) {
        return 1.0f;
    }
    return fabsf(s->stick_throttle - s->motor_output);
}

fm_deny_t fm_throttle_interlock(fm_mode_t current, fm_mode_t target,
                                const fm_state_t *s, const fm_params_t *p,
                                bool in_air)
{
    if (!s || !p) {
        return FM_DENY_INVALID_MODE;
    }

    /* На землі стрибок газу нічим не загрожує: тяга й так на холостому ходу,
       а вимагати від пілота зводити ручку перед зльотом — марно дратувати. */
    if (!in_air || !s->armed) {
        return FM_ALLOW;
    }

    if (!fm_mode_auto_throttle(current) || !fm_mode_manual_throttle(target)) {
        return FM_ALLOW;
    }

    if (fm_throttle_mismatch(s) > p->throttle_deadband) {
        return FM_DENY_THROTTLE_MISMATCH;
    }
    return FM_ALLOW;
}

void fm_slew_reset(fm_slew_t *sl, float value)
{
    if (!sl) {
        return;
    }
    sl->output = value;
    sl->primed = true;
}

float fm_slew_step(fm_slew_t *sl, float target, float dt_s, float rate_per_s)
{
    if (!sl) {
        return target;
    }
    if (!sl->primed) {
        fm_slew_reset(sl, target);
        return sl->output;
    }
    if (!(dt_s > 0.0f) || !(rate_per_s > 0.0f)) {
        /* Нульовий такт або вимкнене обмеження — пропускаємо як є, але стан
           усе одно оновлюємо, щоб наступний крок рахувався від правди. */
        sl->output = target;
        return sl->output;
    }

    const float max_step = rate_per_s * dt_s;
    const float delta    = target - sl->output;

    if (delta > max_step) {
        sl->output += max_step;
    } else if (delta < -max_step) {
        sl->output -= max_step;
    } else {
        sl->output = target;
    }

    if (sl->output < 0.0f) {
        sl->output = 0.0f;
    } else if (sl->output > 1.0f) {
        sl->output = 1.0f;
    }
    return sl->output;
}

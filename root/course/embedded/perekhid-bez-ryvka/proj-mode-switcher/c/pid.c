#include "pid.h"

#include <math.h>

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

void pid_init(pid_t *p, const pid_cfg_t *cfg)
{
    p->cfg = *cfg;
    p->integral = 0.0f;
    p->prev_meas = 0.0f;
    p->target_sp = 0.0f;
    p->current_sp = 0.0f;
    p->last_out = 0.0f;
    p->ready = false;
    p->bad_samples = 0;
}

float pid_bumpless_handover(pid_t *p, float meas, float meas_rate,
                            float target_sp, float prev_out)
{
    if (!isfinite(meas) || !isfinite(prev_out)) {
        /* Захопити нема від чого: без справжнього виміру ми не знаємо,
           яким має бути нуль помилки. Контур лишається неготовим. */
        p->bad_samples++;
        p->ready = false;
        return NAN;
    }

    const float rate = isfinite(meas_rate) ? meas_rate : 0.0f;

    p->current_sp = meas;   /* уставка = поточний вимір, отже помилка рівно нуль */
    p->target_sp  = isfinite(target_sp) ? target_sp : meas;
    p->prev_meas  = meas;

    const float p_term  = p->cfg.kp * (p->current_sp - meas);  /* тотожний нуль */
    const float ff_term = p->cfg.kff * p->current_sp;
    const float d_term  = -p->cfg.kd * rate;   /* саме стільки дасть D на першому такті */

    /* Інтегратор добираємо так, щоб сума всіх гілок дала рівно те, що вже
       стоїть на приводі. Це і є безривкова передача повноважень. */
    const float needed_i = prev_out - p_term - ff_term - d_term;
    p->integral = clampf(needed_i, p->cfg.i_min, p->cfg.i_max);

    const float u0 = clampf(p_term + p->integral + d_term + ff_term,
                            p->cfg.out_min, p->cfg.out_max);
    p->last_out = u0;
    p->ready = true;
    return u0 - prev_out;
}

void pid_retarget(pid_t *p, float target_sp)
{
    if (isfinite(target_sp)) p->target_sp = target_sp;
}

float pid_update(pid_t *p, float meas, float meas_rate, float dt)
{
    if (!p->ready || !(dt > 0.0f)) return p->last_out;
    if (!isfinite(meas)) {
        /* Пропав вимір — тримаємо останній вихід, не інтегруємо сміття. */
        p->bad_samples++;
        return p->last_out;
    }

    /* Ремпінг уставки: ціль може бути далеко, але рухаємось до неї
       обмеженим темпом, інакше ривок просто переїде з перемикання на ціль. */
    if (p->cfg.slew_rate_max > 0.0f) {
        const float max_step = p->cfg.slew_rate_max * dt;
        const float d = p->target_sp - p->current_sp;
        if (d > max_step)       p->current_sp += max_step;
        else if (d < -max_step) p->current_sp -= max_step;
        else                    p->current_sp = p->target_sp;
    } else {
        p->current_sp = p->target_sp;
    }

    const float err = p->current_sp - meas;
    const float p_term = p->cfg.kp * err;

    const float rate = isfinite(meas_rate) ? meas_rate
                                           : (meas - p->prev_meas) / dt;
    p->prev_meas = meas;
    const float d_term = -p->cfg.kd * rate;   /* похідна по виміру, не по помилці */

    const float ff_term = p->cfg.kff * p->current_sp;
    const float cand_i  = p->integral + p->cfg.ki * err * dt;
    const float u_raw   = p_term + cand_i + d_term + ff_term;

    /* Умовна інтеграція: коли вихід уже вперся, а помилка штовхає далі в
       той самий бік, інтегратор не наливаємо — інакше він не віддасть
       керування назад, коли ситуація зміниться. */
    const bool sat_hi = (u_raw > p->cfg.out_max) && (err > 0.0f);
    const bool sat_lo = (u_raw < p->cfg.out_min) && (err < 0.0f);
    if (!sat_hi && !sat_lo)
        p->integral = clampf(cand_i, p->cfg.i_min, p->cfg.i_max);

    p->last_out = clampf(u_raw, p->cfg.out_min, p->cfg.out_max);
    return p->last_out;
}

float pid_output(const pid_t *p)   { return p->last_out; }
float pid_setpoint(const pid_t *p) { return p->current_sp; }
float pid_integral(const pid_t *p) { return p->integral; }

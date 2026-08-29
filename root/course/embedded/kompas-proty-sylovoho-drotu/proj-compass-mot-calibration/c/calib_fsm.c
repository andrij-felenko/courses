#include "calib_fsm.h"

#include <math.h>
#include <stddef.h>

/* Регламент прогону. Це не конфігурація — це сам протокол із §2,
 * і міняти його на льоту нема кому. */
#define CM_BASELINE_MS      2000u   /* тиша при зупинених моторах        */
#define CM_STEP_PCT         10.0f   /* висота сходинки газу              */
#define CM_STEP_HOLD_MS     1200u   /* витримка на сходинці              */
#define CM_PEAK_PCT         85.0f   /* стеля прогону                     */
#define CM_PEAK_HOLD_MS     1500u
#define CM_DOWN_STEP_MS      300u   /* скид газу — швидший за підйом     */
#define CM_SETTLE_MS         400u   /* поки перехідний процес не вщух —
                                     * вибірок не беремо                 */

/* Безпека стенда. */
#define CM_ZERO_CURRENT_A     1.0f  /* більше цього при 0% газу = зсув нуля шунта */
#define CM_ABORT_CURRENT_A  200.0f  /* понад це — глушимо все            */
#define CM_BASE_MIN_SAMPLES   50u

static void enter(cm_calib_t *c, cm_state_t st, uint32_t now_ms)
{
    c->state = st;
    c->t_state_ms = now_ms;
    c->t_step_ms = now_ms;
}

static void throttle(cm_calib_t *c, float pct)
{
    if (pct < 0.0f) {
        pct = 0.0f;
    } else if (pct > CM_PEAK_PCT) {
        pct = CM_PEAK_PCT;
    }
    c->throttle_pct = pct;
    c->io.set_throttle(c->io.ctx, pct);
}

static void fail(cm_calib_t *c, const char *reason, compass_mot_err_t err, uint32_t now_ms)
{
    throttle(c, 0.0f);           /* перше і головне: зняти газ */
    c->fail_reason = reason;
    c->err = err;
    enter(c, CM_FAILED, now_ms);
}

void cm_calib_abort(cm_calib_t *c, const char *reason)
{
    if (c->state == CM_DONE || c->state == CM_FAILED) {
        return;
    }
    throttle(c, 0.0f);
    c->fail_reason = (reason != NULL) ? reason : "зупинено оператором";
    c->err = COMPASS_MOT_ERR_FEW_SAMPLES;
    c->state = CM_FAILED;
}

void cm_calib_start(cm_calib_t *c, const cm_io_t *io, uint32_t now_ms)
{
    const cm_calib_t empty = {0};
    *c = empty;
    c->io = *io;
    throttle(c, 0.0f);
    enter(c, CM_IDLE, now_ms);
}

/* Спільна для всіх «газованих» станів перевірка й збір вибірки.
 * Повертає false, якщо прогін щойно впав. */
static bool sample_and_guard(cm_calib_t *c, uint32_t now_ms, bool collect)
{
    const float i = c->io.read_current(c->io.ctx);
    const vec3_t b = c->io.read_field(c->io.ctx);

    if (isfinite(i) && i > CM_ABORT_CURRENT_A) {
        fail(c, "струм за межею стенда: глушимо прогін", COMPASS_MOT_ERR_NO_SPAN, now_ms);
        return false;
    }
    if (collect && (now_ms - c->t_step_ms) >= CM_SETTLE_MS) {
        compass_mot_ols_feed(&c->ols, i, b);
    }
    return true;
}

cm_state_t cm_calib_step(cm_calib_t *c, uint32_t now_ms)
{
    switch (c->state) {

    case CM_IDLE:
        throttle(c, 0.0f);
        compass_mot_ols_reset(&c->ols, (vec3_t){0.0f, 0.0f, 0.0f});
        c->base_sum[0] = c->base_sum[1] = c->base_sum[2] = 0.0;
        c->base_n = 0;
        enter(c, CM_BASELINE, now_ms);
        break;

    case CM_BASELINE: {
        const float i = c->io.read_current(c->io.ctx);
        const vec3_t b = c->io.read_field(c->io.ctx);

        /* §5: шунт із температурним зсувом нуля зсуне все калібрування.
         * Ловимо це тут, поки мотори ще стоять. */
        if (isfinite(i) && fabsf(i) > CM_ZERO_CURRENT_A) {
            fail(c, "давач струму показує струм при зупинених моторах: "
                    "спершу відкалібрувати зсув нуля шунта",
                 COMPASS_MOT_ERR_NO_SPAN, now_ms);
            break;
        }
        if (isfinite(b.x) && isfinite(b.y) && isfinite(b.z)) {
            c->base_sum[0] += b.x;
            c->base_sum[1] += b.y;
            c->base_sum[2] += b.z;
            c->base_n++;
        }

        if ((now_ms - c->t_state_ms) < CM_BASELINE_MS) {
            break;
        }
        if (c->base_n < CM_BASE_MIN_SAMPLES) {
            fail(c, "магнітометр майже не віддає даних", COMPASS_MOT_ERR_NO_FIELD, now_ms);
            break;
        }

        const float n = (float)c->base_n;
        const vec3_t base = {
            (float)(c->base_sum[0] / n),
            (float)(c->base_sum[1] / n),
            (float)(c->base_sum[2] / n),
        };
        compass_mot_ols_reset(&c->ols, base);

        throttle(c, CM_STEP_PCT);
        enter(c, CM_RAMP_UP, now_ms);
        break;
    }

    case CM_RAMP_UP:
        if (!sample_and_guard(c, now_ms, true)) {
            break;
        }
        if ((now_ms - c->t_step_ms) < CM_STEP_HOLD_MS) {
            break;
        }
        if (c->throttle_pct >= CM_PEAK_PCT - 0.5f) {
            enter(c, CM_PEAK_HOLD, now_ms);
            break;
        }
        throttle(c, c->throttle_pct + CM_STEP_PCT);
        c->t_step_ms = now_ms;      /* нова сходинка — нова пауза на усталення */
        break;

    case CM_PEAK_HOLD:
        if (!sample_and_guard(c, now_ms, true)) {
            break;
        }
        if ((now_ms - c->t_state_ms) >= CM_PEAK_HOLD_MS) {
            throttle(c, c->throttle_pct - CM_STEP_PCT);
            enter(c, CM_RAMP_DOWN, now_ms);
        }
        break;

    case CM_RAMP_DOWN:
        /* На спуску вибірок НЕ беремо: ключі й дроти вже прогрілися,
         * і гістерезис намагніченості поруч із компасом додав би в дані
         * систематичний зсув, якого модель не описує. */
        if (!sample_and_guard(c, now_ms, false)) {
            break;
        }
        if ((now_ms - c->t_step_ms) < CM_DOWN_STEP_MS) {
            break;
        }
        if (c->throttle_pct <= 0.5f) {
            throttle(c, 0.0f);
            enter(c, CM_SOLVE, now_ms);
            break;
        }
        throttle(c, c->throttle_pct - CM_STEP_PCT);
        c->t_step_ms = now_ms;
        break;

    case CM_SOLVE: {
        const compass_mot_err_t err = compass_mot_ols_solve(&c->ols, &c->fit);
        if (err != COMPASS_MOT_OK) {
            fail(c, compass_mot_strerror(err), err, now_ms);
            break;
        }
        enter(c, CM_SAVE, now_ms);
        break;
    }

    case CM_SAVE:
        if (!c->io.save_params(c->io.ctx, c->fit.k)) {
            fail(c, compass_mot_strerror(COMPASS_MOT_ERR_SAVE),
                 COMPASS_MOT_ERR_SAVE, now_ms);
            break;
        }
        enter(c, CM_DONE, now_ms);
        break;

    case CM_DONE:
    case CM_FAILED:
        break;
    }

    return c->state;
}

const char *cm_state_name(cm_state_t st)
{
    switch (st) {
    case CM_IDLE:      return "IDLE";
    case CM_BASELINE:  return "BASELINE";
    case CM_RAMP_UP:   return "RAMP UP";
    case CM_PEAK_HOLD: return "PEAK HOLD";
    case CM_RAMP_DOWN: return "RAMP DOWN";
    case CM_SOLVE:     return "OLS SOLVE";
    case CM_SAVE:      return "FLASH SAVE";
    case CM_DONE:      return "DONE";
    case CM_FAILED:    return "FAILED";
    }
    return "?";
}

#include "admittance.h"

#include <math.h>

#define ADM_PI 3.14159265358979f

float admittance_alpha_for_cutoff(float cutoff_hz)
{
    if (!(cutoff_hz > 0.0f)) {
        return 1.0f; /* фільтр вимкнено */
    }
    const float rc = 1.0f / (2.0f * ADM_PI * cutoff_hz);
    return ADM_DT_SEC / (rc + ADM_DT_SEC);
}

void admittance_set_critical_damping(admittance_config_t *cfg)
{
    if (!cfg) {
        return;
    }
    for (int i = 0; i < ADM_DOF; ++i) {
        cfg->d_d[i] = 2.0f * sqrtf(cfg->m_d[i] * cfg->k_d[i]);
    }
}

bool admittance_config_valid(const admittance_config_t *cfg)
{
    if (!cfg) {
        return false;
    }
    if (!(cfg->filter_alpha > 0.0f) || cfg->filter_alpha > 1.0f) {
        return false;
    }
    if (!(cfg->retract_speed > 0.0f)) {
        return false;
    }
    for (int i = 0; i < ADM_DOF; ++i) {
        /* На масу ділимо щотакту — нуль тут це NaN у команді приводам. */
        if (!(cfg->m_d[i] > 0.0f)) {
            return false;
        }
        if (cfg->d_d[i] < 0.0f || cfg->k_d[i] < 0.0f) {
            return false;
        }
        if (!(cfg->max_disp[i] > 0.0f) || !(cfg->max_vel[i] > 0.0f)) {
            return false;
        }
        if (cfg->deadband[i] < 0.0f || !(cfg->max_force[i] > cfg->deadband[i])) {
            return false;
        }
    }
    return true;
}

void admittance_init(admittance_context_t *ctx)
{
    if (!ctx) {
        return;
    }
    for (int i = 0; i < ADM_DOF; ++i) {
        ctx->f_raw_offset[i] = 0.0f;
        ctx->f_filt[i] = 0.0f;
        ctx->disp[i] = 0.0f;
        ctx->vel[i] = 0.0f;
        ctx->retract_dir[i] = 0.0f;
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_MODE_IDLE;
}

void admittance_start_tare(admittance_context_t *ctx)
{
    if (!ctx) {
        return;
    }
    for (int i = 0; i < ADM_DOF; ++i) {
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_MODE_TARING;
}

void admittance_acknowledge(admittance_context_t *ctx)
{
    if (!ctx || ctx->mode != ADMITTANCE_MODE_RETRACT) {
        return;
    }
    for (int i = 0; i < ADM_DOF; ++i) {
        ctx->vel[i] = 0.0f;
        ctx->retract_dir[i] = 0.0f;
    }
    ctx->mode = ADMITTANCE_MODE_ACTIVE;
}

/* Стояти на номіналі, тримаючи вже набране зміщення: IDLE і FAULT. */
static void hold_outputs(const admittance_context_t *ctx,
                         const float x_nominal[ADM_DOF],
                         float x_cmd[ADM_DOF],
                         float v_cmd[ADM_DOF])
{
    for (int i = 0; i < ADM_DOF; ++i) {
        x_cmd[i] = x_nominal[i] + ctx->disp[i];
        v_cmd[i] = 0.0f;
    }
}

static admittance_mode_t step_tare(const admittance_config_t *cfg,
                                   admittance_context_t *ctx,
                                   const float f_ext[ADM_DOF],
                                   const float x_nominal[ADM_DOF],
                                   const float v_nominal[ADM_DOF],
                                   float x_cmd[ADM_DOF],
                                   float v_cmd[ADM_DOF])
{
    for (int i = 0; i < ADM_DOF; ++i) {
        /* Тарування має відбуватися у вільному просторі. Якщо інструмент
           уже щось торкає, усереднений «нуль» піде в роботу як зсув — і
           контролер тихо працюватиме з хибною силою весь сеанс. */
        if (fabsf(f_ext[i]) > cfg->max_force[i]) {
            ctx->mode = ADMITTANCE_MODE_FAULT;
            hold_outputs(ctx, x_nominal, x_cmd, v_cmd);
            return ctx->mode;
        }
        ctx->tare_accumulator[i] += f_ext[i];
        x_cmd[i] = x_nominal[i];
        v_cmd[i] = v_nominal[i];
    }

    if (++ctx->tare_counter >= ADM_TARE_SAMPLES) {
        for (int i = 0; i < ADM_DOF; ++i) {
            ctx->f_raw_offset[i] = ctx->tare_accumulator[i] / (float)ADM_TARE_SAMPLES;
            ctx->f_filt[i] = 0.0f;
            ctx->disp[i] = 0.0f;
            ctx->vel[i] = 0.0f;
        }
        ctx->mode = ADMITTANCE_MODE_ACTIVE;
    }
    return ctx->mode;
}

/* Напрямок аварійного відходу — уздовж нормалі контакту, тобто протилежно
   виміряній силі реакції. Обертання при відході не чіпаємо. */
static void latch_retract_direction(admittance_context_t *ctx)
{
    for (int i = 0; i < ADM_DOF; ++i) {
        ctx->retract_dir[i] = 0.0f;
    }
    const float norm = sqrtf(ctx->f_filt[0] * ctx->f_filt[0] +
                             ctx->f_filt[1] * ctx->f_filt[1] +
                             ctx->f_filt[2] * ctx->f_filt[2]);
    if (norm < 1.0e-6f) {
        return; /* перевищив момент, а не сила — відходити нікуди */
    }
    for (int i = 0; i < 3; ++i) {
        ctx->retract_dir[i] = -ctx->f_filt[i] / norm;
    }
}

static admittance_mode_t step_retract(const admittance_config_t *cfg,
                                      admittance_context_t *ctx,
                                      const float x_nominal[ADM_DOF],
                                      float x_cmd[ADM_DOF],
                                      float v_cmd[ADM_DOF])
{
    ctx->mode = ADMITTANCE_MODE_RETRACT;
    for (int i = 0; i < ADM_DOF; ++i) {
        float delta = ctx->retract_dir[i] * cfg->retract_speed * ADM_DT_SEC;
        float next = ctx->disp[i] + delta;
        if (next > cfg->max_disp[i]) {
            next = cfg->max_disp[i];
            delta = 0.0f;
        } else if (next < -cfg->max_disp[i]) {
            next = -cfg->max_disp[i];
            delta = 0.0f;
        }
        ctx->disp[i] = next;
        ctx->vel[i] = delta / ADM_DT_SEC;
        /* Номінальну траєкторію в аварії скасовано: рухаємось лише від деталі. */
        x_cmd[i] = x_nominal[i] + ctx->disp[i];
        v_cmd[i] = ctx->vel[i];
    }
    return ctx->mode;
}

static admittance_mode_t step_active(const admittance_config_t *cfg,
                                     admittance_context_t *ctx,
                                     const float f_ext[ADM_DOF],
                                     const float x_nominal[ADM_DOF],
                                     const float v_nominal[ADM_DOF],
                                     float x_cmd[ADM_DOF],
                                     float v_cmd[ADM_DOF])
{
    /* 1. Зняття нуля і фільтрація — по ВСІХ осях, перш ніж щось вирішувати.
       Інакше при спрацюванні ліміту на осі X стан фільтра осей Y..Tz
       лишився б від попереднього такту й наступний вхід у контур
       почався б із застарілої сили. */
    bool exceeded = false;
    for (int i = 0; i < ADM_DOF; ++i) {
        const float f_unbiased = f_ext[i] - ctx->f_raw_offset[i];
        ctx->f_filt[i] = (1.0f - cfg->filter_alpha) * ctx->f_filt[i] +
                         cfg->filter_alpha * f_unbiased;
        if (fabsf(ctx->f_filt[i]) > cfg->max_force[i]) {
            exceeded = true;
        }
    }

    /* 2. Скінченний автомат безпеки. */
    if (exceeded) {
        latch_retract_direction(ctx);
        for (int i = 0; i < ADM_DOF; ++i) {
            ctx->vel[i] = 0.0f;
            x_cmd[i] = x_nominal[i] + ctx->disp[i];
            v_cmd[i] = 0.0f;
        }
        ctx->mode = ADMITTANCE_MODE_FORCE_EXCEEDED;
        return ctx->mode;
    }

    for (int i = 0; i < ADM_DOF; ++i) {
        /* 3. Зона нечутливості: шум давача не має інтегруватися в дрейф. */
        float f_active = 0.0f;
        if (ctx->f_filt[i] > cfg->deadband[i]) {
            f_active = ctx->f_filt[i] - cfg->deadband[i];
        } else if (ctx->f_filt[i] < -cfg->deadband[i]) {
            f_active = ctx->f_filt[i] + cfg->deadband[i];
        }

        /* 4. Динаміка адмітансу: M_d·a + D_d·v + K_d·p = −F. */
        const float accel = (-f_active - cfg->d_d[i] * ctx->vel[i] -
                             cfg->k_d[i] * ctx->disp[i]) / cfg->m_d[i];

        /* Напівнеявний Ейлер: координата інтегрується вже НОВОЮ швидкістю. */
        ctx->vel[i] += accel * ADM_DT_SEC;
        if (ctx->vel[i] > cfg->max_vel[i]) {
            ctx->vel[i] = cfg->max_vel[i];
        } else if (ctx->vel[i] < -cfg->max_vel[i]) {
            ctx->vel[i] = -cfg->max_vel[i];
        }
        ctx->disp[i] += ctx->vel[i] * ADM_DT_SEC;

        /* 5. Упор ходу з гасінням швидкості в бік упору (anti-windup):
           без цього віртуальна маса накопичувала б кінетичну енергію
           на межі й вистрілювала, щойно сила зникне. */
        if (ctx->disp[i] > cfg->max_disp[i]) {
            ctx->disp[i] = cfg->max_disp[i];
            if (ctx->vel[i] > 0.0f) {
                ctx->vel[i] = 0.0f;
            }
        } else if (ctx->disp[i] < -cfg->max_disp[i]) {
            ctx->disp[i] = -cfg->max_disp[i];
            if (ctx->vel[i] < 0.0f) {
                ctx->vel[i] = 0.0f;
            }
        }

        x_cmd[i] = x_nominal[i] + ctx->disp[i];
        v_cmd[i] = v_nominal[i] + ctx->vel[i];
    }

    ctx->mode = ADMITTANCE_MODE_ACTIVE;
    return ctx->mode;
}

admittance_mode_t admittance_step(const admittance_config_t *cfg,
                                  admittance_context_t *ctx,
                                  const float f_ext[ADM_DOF],
                                  const float x_nominal[ADM_DOF],
                                  const float v_nominal[ADM_DOF],
                                  float x_cmd[ADM_DOF],
                                  float v_cmd[ADM_DOF])
{
    if (!ctx || !f_ext || !x_nominal || !v_nominal || !x_cmd || !v_cmd) {
        return ADMITTANCE_MODE_FAULT;
    }
    if (!admittance_config_valid(cfg)) {
        ctx->mode = ADMITTANCE_MODE_FAULT;
        hold_outputs(ctx, x_nominal, x_cmd, v_cmd);
        return ctx->mode;
    }

    switch (ctx->mode) {
    case ADMITTANCE_MODE_TARING:
        return step_tare(cfg, ctx, f_ext, x_nominal, v_nominal, x_cmd, v_cmd);
    case ADMITTANCE_MODE_FORCE_EXCEEDED:
    case ADMITTANCE_MODE_RETRACT:
        return step_retract(cfg, ctx, x_nominal, x_cmd, v_cmd);
    case ADMITTANCE_MODE_ACTIVE:
        return step_active(cfg, ctx, f_ext, x_nominal, v_nominal, x_cmd, v_cmd);
    case ADMITTANCE_MODE_IDLE:
    case ADMITTANCE_MODE_FAULT:
    default:
        hold_outputs(ctx, x_nominal, x_cmd, v_cmd);
        return ctx->mode;
    }
}

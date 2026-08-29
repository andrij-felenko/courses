#include "supervisor.h"
#include <math.h>

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void stop_command(CommandVector *out)
{
    out->vx = 0.0f;
    out->vy = 0.0f;
    out->yaw_rate = 0.0f;
}

/* Детерміноване лінійне сповільнення: керує сам супервізор, планувальник поза грою. */
static SafetyStatus engage_brake(SafetySupervisor *s, float dt, CommandVector *out,
                                 BbReason reason, float value)
{
    const float decel = MAX_BRAKE_ACCEL_MPS2 * dt;
    s->last_out_vx = (s->last_out_vx > decel) ? (s->last_out_vx - decel) : 0.0f;

    out->vx = s->last_out_vx;
    out->vy = 0.0f;
    out->yaw_rate = 0.0f;

    blackbox_record(&s->log, s->current_tick, s->uptime_s,
                    (uint8_t)SAFETY_BRAKE_ENGAGED, (uint8_t)reason, value);
    return SAFETY_BRAKE_ENGAGED;
}

/* Fail-closed: коли далекомір мовчить або бреше, бар'єр НЕ вважає простір вільним.
 * Замість виміру береться остання достовірна дистанція мінус пройдений шлях
 * (інерціальне числення), тож оцінка з часом лише погіршується. */
static float update_distance_estimate(SafetySupervisor *s, const SensorEnvelope *sn, float dt)
{
    const bool sane = sn->obstacle_dist_valid
                   && isfinite(sn->obstacle_dist_m)
                   && sn->obstacle_dist_m >= 0.0f;

    if (sane) {
        s->dr_dist_m = sn->obstacle_dist_m;
        s->dr_elapsed_s = 0.0f;
        s->dist_trusted = true;
        return s->dr_dist_m;
    }

    s->dr_dist_m -= s->last_out_vx * dt;
    if (s->dr_dist_m < 0.0f) s->dr_dist_m = 0.0f;
    s->dr_elapsed_s += dt;
    s->dist_trusted = false;
    return s->dr_dist_m;
}

void safety_init(SafetySupervisor *s)
{
    if (!s) return;

    s->current_tick = 0u;
    s->last_plan_tick = 0u;
    s->candidate.vx = 0.0f;
    s->candidate.vy = 0.0f;
    s->candidate.yaw_rate = 0.0f;
    s->last_out_vx = 0.0f;
    s->dr_dist_m = 0.0f;      /* до першого виміру простір вважається зайнятим */
    s->dr_elapsed_s = SENSOR_HOLD_MAX_SEC;
    s->dist_trusted = false;
    s->uptime_s = 0.0f;
    blackbox_init(&s->log);
}

bool safety_submit_plan(SafetySupervisor *s, const CommandVector *cmd)
{
    if (!s || !cmd) return false;

    if (!isfinite(cmd->vx) || !isfinite(cmd->vy) || !isfinite(cmd->yaw_rate)) {
        /* NaN у пакеті — уставку викидаємо цілком і свіжості не оновлюємо */
        blackbox_record(&s->log, s->current_tick, s->uptime_s,
                        (uint8_t)SAFETY_CLAMPED, (uint8_t)BB_REASON_BAD_PLAN, 0.0f);
        return false;
    }

    s->candidate = *cmd;
    s->last_plan_tick = s->current_tick;
    return true;
}

SafetyStatus safety_step(SafetySupervisor *s, const SensorEnvelope *sn,
                         float dt, CommandVector *out)
{
    if (!s || !sn || !out) return SAFETY_ESTOP_ACTIVE;

    if (!isfinite(dt) || dt <= 0.0f) {
        /* Зламаний такт — не місце для арифметики: нуль на приводи */
        stop_command(out);
        s->last_out_vx = 0.0f;
        return SAFETY_ESTOP_ACTIVE;
    }

    s->current_tick++;
    s->uptime_s += dt;

    /* 1. Апаратна кнопка стоїть вище за будь-яку логіку */
    if (sn->emergency_switch) {
        stop_command(out);
        s->last_out_vx = 0.0f;
        blackbox_record(&s->log, s->current_tick, s->uptime_s,
                        (uint8_t)SAFETY_ESTOP_ACTIVE, (uint8_t)BB_REASON_ESTOP, 0.0f);
        return SAFETY_ESTOP_ACTIVE;
    }

    /* 2. Дистанція: або вимір, або консервативне числення */
    const float dist = update_distance_estimate(s, sn, dt);

    /* 3. Крен. Зіпсований вимір кута — теж підстава гальмувати */
    const float tilt = sn->current_tilt_rad;
    const float tilt_limit = sn->max_tilt_limit;
    if (!isfinite(tilt) || !isfinite(tilt_limit) || tilt_limit <= 0.0f) {
        return engage_brake(s, dt, out, BB_REASON_SENSOR_LOST, tilt);
    }
    if (tilt >= tilt_limit) {
        return engage_brake(s, dt, out, BB_REASON_TILT, tilt);
    }

    /* 4. Сторож планувальника: уставка застаріла — керуємо самі */
    const uint32_t plan_age = s->current_tick - s->last_plan_tick;
    if (plan_age > WATCHDOG_MAX_TICKS) {
        return engage_brake(s, dt, out, BB_REASON_WATCHDOG, (float)plan_age * dt);
    }

    /* 5. Невизначеність дистанції довша за допуск — плавна зупинка */
    if (!s->dist_trusted && s->dr_elapsed_s >= SENSOR_HOLD_MAX_SEC) {
        return engage_brake(s, dt, out, BB_REASON_SENSOR_LOST, s->dr_elapsed_s);
    }

    /* Далі — проєкція уставки на допустиму область. Кожен крок лише зменшує
     * дозволене, тож остання спрацьована причина і є найтіснішою. */
    float target_vx = s->candidate.vx;
    float target_yaw = s->candidate.yaw_rate;
    if (target_vx < 0.0f) target_vx = 0.0f; /* задній хід у цій моделі не розглядаємо */

    BbReason reason = BB_REASON_NONE;
    float violated = 0.0f;

    /* 6. Гальмівний бар'єр за дистанцією */
    const float stop_dist = (target_vx * target_vx) / (2.0f * MAX_BRAKE_ACCEL_MPS2)
                          + target_vx * LATENCY_PAD_SEC
                          + SAFETY_MARGIN_M;
    if (dist < stop_dist) {
        const float available = dist - SAFETY_MARGIN_M;
        const float v_max_safe = (available <= 0.0f)
                               ? 0.0f
                               : sqrtf(2.0f * MAX_BRAKE_ACCEL_MPS2 * available);
        if (target_vx > v_max_safe) {
            target_vx = v_max_safe;
            reason = BB_REASON_OBSTACLE;
            violated = dist;
        }
    }

    /* 7. Просідання шини: униз ідуть і швидкість, і темп розгону */
    float v_factor = 1.0f;
    if (!isfinite(sn->battery_voltage)) {
        v_factor = 0.0f; /* вимірювача напруги нема — рахуємо найгірше */
        reason = BB_REASON_SENSOR_LOST;
        violated = 0.0f;
    } else if (sn->battery_voltage < NOMINAL_VOLTAGE_V) {
        v_factor = clampf((sn->battery_voltage - CRITICAL_VOLTAGE_V)
                          / (NOMINAL_VOLTAGE_V - CRITICAL_VOLTAGE_V), 0.0f, 1.0f);
    }
    if (v_factor < 1.0f) {
        const float max_bat_vx = MAX_ALLOWED_SPEED_MPS * v_factor;
        if (target_vx > max_bat_vx) {
            target_vx = max_bat_vx;
            reason = BB_REASON_BATTERY;
            violated = sn->battery_voltage;
        }
    }

    /* 8. Підхід до критичного крену: тиснемо рискання й хід разом */
    const float tilt_warn = tilt_limit * TILT_WARN_FRACTION;
    if (tilt > tilt_warn) {
        const float headroom = tilt_limit - tilt_warn;
        const float scale = clampf((tilt_limit - tilt) / headroom, 0.0f, 1.0f);
        target_yaw *= scale;
        target_vx *= scale;
        reason = BB_REASON_TILT;
        violated = tilt;
    }

    /* 9. Абсолютні межі приводів */
    if (target_vx > MAX_ALLOWED_SPEED_MPS) {
        target_vx = MAX_ALLOWED_SPEED_MPS;
        reason = BB_REASON_SPEED_LIMIT;
        violated = s->candidate.vx;
    }
    const float yaw_clamped = clampf(target_yaw, -MAX_YAW_RATE_RADPS, MAX_YAW_RATE_RADPS);
    if (yaw_clamped != target_yaw) {
        target_yaw = yaw_clamped;
        if (reason == BB_REASON_NONE) {
            reason = BB_REASON_YAW_LIMIT;
            violated = s->candidate.yaw_rate;
        }
    }

    /* 10. Темп розгону за струмовим бюджетом. Сповільнення не обмежуємо:
     *     у бік безпеки фільтр працює миттєво. */
    const float accel_cap = MAX_ACCEL_MPS2 * v_factor;
    const float max_step = accel_cap * dt;
    if (target_vx > s->last_out_vx + max_step) {
        target_vx = s->last_out_vx + max_step;
        if (reason == BB_REASON_NONE) {
            reason = BB_REASON_ACCEL_LIMIT;
            violated = accel_cap;
        }
    }

    out->vx = target_vx;
    out->vy = s->candidate.vy;
    out->yaw_rate = target_yaw;
    s->last_out_vx = target_vx;

    const SafetyStatus status = (reason == BB_REASON_NONE)
                              ? SAFETY_PASS_THROUGH
                              : SAFETY_CLAMPED;
    blackbox_record(&s->log, s->current_tick, s->uptime_s,
                    (uint8_t)status, (uint8_t)reason, violated);
    return status;
}

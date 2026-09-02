#include "safety_arbiter.h"

#include <math.h>

/* --- дрібна векторна арифметика (без купи й без бібліотек) --------------- */

static Vec2 vec2_zero(void)
{
    Vec2 r = { 0.0f, 0.0f };
    return r;
}

static Vec2 vec2_add(Vec2 a, Vec2 b)
{
    Vec2 r = { a.x + b.x, a.y + b.y };
    return r;
}

static Vec2 vec2_scale(Vec2 v, float s)
{
    Vec2 r = { v.x * s, v.y * s };
    return r;
}

static float vec2_len(Vec2 v)
{
    return sqrtf(v.x * v.x + v.y * v.y);
}

static bool vec2_finite(Vec2 v)
{
    return isfinite(v.x) && isfinite(v.y);
}

Vec2 safety_odom_to_body(Vec2 v, float yaw_rad)
{
    const float c = cosf(yaw_rad);
    const float s = sinf(yaw_rad);
    Vec2 r = { c * v.x + s * v.y, -s * v.x + c * v.y };
    return r;
}

const char *safety_zone_name(SafetyZone zone)
{
    switch (zone) {
        case ZONE_ESTOP:   return "ESTOP";
        case ZONE_WARNING: return "WARNING";
        default:           return "OBSERVATION";
    }
}

/* --- ініціалізація ------------------------------------------------------- */

bool safety_arbiter_init(SafetyArbiter *arb, const SafetyParams *params)
{
    if (arb == NULL || params == NULL) {
        return false;
    }
    /* Порівняння «> 0.05f» відсіює і нуль, і від'ємне, і NaN одним рухом:
       будь-яке порівняння з NaN хибне. */
    if (!(params->max_accel > 0.05f)) {
        return false;
    }
    if (!(params->planner_period > 0.0f) || !(params->reaction_time >= 0.0f)) {
        return false;
    }
    if (!(params->stop_margin >= 0.0f) || !(params->warn_buffer >= 0.0f)) {
        return false;
    }

    arb->params = *params;
    arb->current_zone = ZONE_OBSERVATION;
    arb->hold_counter = SAFETY_HOLD_TICKS;
    arb->planner_watchdog = 0;
    arb->last_cmd_vel = vec2_zero();
    arb->planner_timed_out = false;

    /* Поріг сторожа рахуємо з періоду планувальника, а не прошиваємо числом:
       поміняли планувальник з 5 Гц на 2 Гц — арбітр підлаштувався сам. */
    const float limit = (SAFETY_WATCHDOG_K * params->planner_period) / SAFETY_DT_SEC;
    arb->watchdog_limit = (limit < 2.0f) ? 2u : (uint32_t)limit;
    return true;
}

void safety_arbiter_planner_heartbeat(SafetyArbiter *arb)
{
    if (arb == NULL) {
        return;
    }
    arb->planner_watchdog = 0;
    arb->planner_timed_out = false;
}

/* --- автомат переходів --------------------------------------------------- */

static SafetyZone zone_of(float dist, float r_stop, float r_warn)
{
    if (dist <= r_stop) {
        return ZONE_ESTOP;
    }
    if (dist <= r_warn) {
        return ZONE_WARNING;
    }
    return ZONE_OBSERVATION;
}

static void step_state_machine(SafetyArbiter *arb, SafetyZone target,
                               float dist, float r_stop, float r_warn)
{
    if (target > arb->current_zone) {
        /* Ескалація миттєва: у бік більшої небезпеки не зволікаємо ніколи. */
        arb->current_zone = target;
        arb->hold_counter = SAFETY_HOLD_TICKS;
        return;
    }

    if (target < arb->current_zone) {
        /* Деескалація: спершу просторовий запас понад поріг, з якого виходимо. */
        bool hyst_cleared = false;
        if (arb->current_zone == ZONE_ESTOP) {
            hyst_cleared = (dist > (r_stop + SAFETY_HYST_DIST_M));
        } else if (arb->current_zone == ZONE_WARNING) {
            hyst_cleared = (dist > (r_warn + SAFETY_HYST_DIST_M));
        }

        if (!hyst_cleared) {
            arb->hold_counter = SAFETY_HOLD_TICKS;
            return;
        }
        /* А тоді ще й витримка часом: одного «чистого» такту мало,
           бо шум давача на кущах дає такі такти пачками. */
        if (arb->hold_counter > 0u) {
            arb->hold_counter--;
        } else {
            arb->current_zone = target;
            arb->hold_counter = SAFETY_HOLD_TICKS;
        }
        return;
    }

    arb->hold_counter = SAFETY_HOLD_TICKS;
}

/* --- такт ---------------------------------------------------------------- */

SafetyOutput safety_arbiter_update(SafetyArbiter *arb, const SafetyInput *in)
{
    SafetyOutput out;
    out.v_cmd = vec2_zero();
    out.zone = ZONE_ESTOP;
    out.alpha = 1.0f;
    out.r_stop = 0.0f;
    out.r_warn = 0.0f;
    out.v_safe = 0.0f;
    out.override_active = true;
    out.planner_timed_out = true;

    if (arb == NULL || in == NULL) {
        return out; /* найбезпечніша відповідь на зламаний виклик — стоп */
    }

    /* 0. Сторож зв'язку з планувальником. */
    if (arb->planner_watchdog < UINT32_MAX) {
        arb->planner_watchdog++;
    }
    Vec2 v_plan = vec2_finite(in->v_plan) ? in->v_plan : vec2_zero();
    if (arb->planner_watchdog > arb->watchdog_limit) {
        arb->planner_timed_out = true;
        v_plan = vec2_zero(); /* без свіжого плану їхати нікуди */
    }
    const Vec2 v_react = vec2_finite(in->v_react) ? in->v_react : vec2_zero();

    /* 1. Санітарний фільтр входів. Несправний далекомір — це не «вільно»,
          а перешкода впритул: єдина безпечна інтерпретація мовчання. */
    const bool range_ok = in->range_valid && (in->min_range_m >= 0.0f);
    const float dist = range_ok ? in->min_range_m : 0.0f;
    const float speed = (in->current_speed > 0.0f) ? in->current_speed : 0.0f;

    /* 2. Динамічні межі зон за гальмівною кінематикою. */
    const float d_brake = (speed * speed) / (2.0f * arb->params.max_accel);
    const float r_stop = d_brake + speed * arb->params.reaction_time + arb->params.stop_margin;
    const float r_warn = r_stop + speed * arb->params.planner_period + arb->params.warn_buffer;

    /* 3. Автомат із просторово-часовим гістерезисом. */
    step_state_machine(arb, zone_of(dist, r_stop, r_warn), dist, r_stop, r_warn);

    /* 4. Формування уставки. */
    Vec2 cmd = vec2_zero();
    float alpha = 0.0f;
    float v_safe = 0.0f;
    bool override_active = false;

    switch (arb->current_zone) {
        case ZONE_ESTOP:
            /* Прапорець потрібен не лише моторам: за ним низовий ПІ-регулятор
               зобов'язаний обнулити інтеграл, інакше на виході з аварії буде ривок. */
            override_active = true;
            alpha = 1.0f;
            cmd = vec2_zero();
            break;

        case ZONE_WARNING: {
            const float span = r_warn - r_stop;
            /* span вироджується в нуль лише при warn_buffer = 0 і нульовій швидкості;
               тоді змішувати нічого — віддаємо рефлексу все. */
            alpha = (span > 1e-3f) ? ((r_warn - dist) / span) : 1.0f;
            if (alpha < 0.0f) alpha = 0.0f;
            if (alpha > 1.0f) alpha = 1.0f;

            cmd = vec2_add(vec2_scale(v_plan, 1.0f - alpha), vec2_scale(v_react, alpha));

            const float dist_to_stop = dist - r_stop;
            if (dist_to_stop > 0.0f) {
                v_safe = sqrtf(2.0f * arb->params.max_accel * dist_to_stop);
                const float cmd_len = vec2_len(cmd);
                /* Зрізаємо модуль, зберігаючи напрямок: інакше зникає сам маневр. */
                if (cmd_len > v_safe && cmd_len > 1e-3f) {
                    cmd = vec2_scale(cmd, v_safe / cmd_len);
                }
            } else {
                cmd = vec2_zero();
            }
            break;
        }

        case ZONE_OBSERVATION:
        default:
            alpha = 0.0f;
            cmd = v_plan;
            break;
    }

    arb->last_cmd_vel = cmd;

    out.v_cmd = cmd;
    out.zone = arb->current_zone;
    out.alpha = alpha;
    out.r_stop = r_stop;
    out.r_warn = r_warn;
    out.v_safe = v_safe;
    out.override_active = override_active;
    out.planner_timed_out = arb->planner_timed_out;
    return out;
}

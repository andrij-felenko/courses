#include "flight_manager.h"

#include <math.h>

#include "dshot.h"

#define STICK_MATCH_WINDOW 0.03f   /* ±3 % навколо утримуваної тяги */
#define YAW_RATE_MAX_DPS   45.0f   /* обмежений темп розвороту на базу */
#define HANDOVER_TOL       0.005f  /* більший стрибок вважаємо за зауваження */

static float wrap180(float a)
{
    while (a > 180.0f)  a -= 360.0f;
    while (a < -180.0f) a += 360.0f;
    return a;
}

static float heading_step(float cur, float target, float rate_dps, float dt)
{
    float d = wrap180(target - cur);
    const float max_step = rate_dps * dt;
    if (d > max_step)       d = max_step;
    else if (d < -max_step) d = -max_step;
    float r = cur + d;
    if (r < 0.0f)      r += 360.0f;
    if (r >= 360.0f)   r -= 360.0f;
    return r;
}

void fm_init(flight_manager_t *m, float home_alt_m, float home_bearing_deg)
{
    m->mode = MODE_MANUAL;
    m->last_out = 0.0f;
    m->stick_hold = false;
    m->u_hold = 0.0f;
    m->failsafe = false;
    m->armed = false;
    m->mission_alt_m = home_alt_m;
    m->home_alt_m = home_alt_m;
    m->home_bearing_deg = home_bearing_deg;
    m->heading_cmd_deg = 0.0f;
    m->handover_warnings = 0;
    m->rejected_switches = 0;

    /* Утримання висоти: спокійний контур, набір не швидше 2 м/с. */
    const pid_cfg_t alt_cfg = {
        .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 2.0f
    };
    pid_init(&m->alt_pid, &alt_cfg);

    /* Маршрутний контур: жвавіший, набір до 3.5 м/с. */
    const pid_cfg_t mission_cfg = {
        .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 3.5f
    };
    pid_init(&m->mission_pid, &mission_cfg);
}

void fm_set_armed(flight_manager_t *m, bool armed) { m->armed = armed; }

void fm_set_mission_target(flight_manager_t *m, float alt_m)
{
    if (!isfinite(alt_m)) return;
    m->mission_alt_m = alt_m;
    if (m->mode == MODE_AUTO_MISSION) pid_retarget(&m->mission_pid, alt_m);
}

bool fm_request_mode(flight_manager_t *m, flight_mode_t mode, const vehicle_state_t *st)
{
    if (mode == m->mode) return true;

    const float prev_out = m->last_out;
    float residual = 0.0f;

    switch (mode) {
    case MODE_MANUAL:
        /* Ручка пілота може стояти будь-де. Доки вона не зійдеться з
           поточною тягою, керування тримає диспетчер. */
        m->stick_hold = true;
        m->u_hold = prev_out;
        break;

    case MODE_ALT_HOLD:
        residual = pid_bumpless_handover(&m->alt_pid, st->alt_m, st->climb_mps,
                                         st->alt_m, prev_out);
        break;

    case MODE_AUTO_MISSION:
        /* Стартуємо з поточної висоти, ціль — точка маршруту; ремпінг
           уставки доведе туди без ривка. */
        residual = pid_bumpless_handover(&m->mission_pid, st->alt_m, st->climb_mps,
                                         m->mission_alt_m, prev_out);
        m->heading_cmd_deg = st->heading_deg;
        break;

    default:
        return false;
    }

    if (isnan(residual)) {
        /* Захоплення не вийшло — лишаємось у чинному режимі, це безпечніше
           за перехід із невідомим станом інтегратора. */
        m->rejected_switches++;
        return false;
    }
    if (fabsf(residual) > HANDOVER_TOL) m->handover_warnings++;

    m->mode = mode;
    return true;
}

void fm_enter_failsafe(flight_manager_t *m, const vehicle_state_t *st)
{
    if (m->failsafe) return;
    m->failsafe = true;

    /* Висота старту стає ціллю, поточний курс — початком розвороту. */
    m->mission_alt_m = m->home_alt_m;
    if (m->mode == MODE_AUTO_MISSION) {
        pid_retarget(&m->mission_pid, m->mission_alt_m);
    } else {
        fm_request_mode(m, MODE_AUTO_MISSION, st);
    }
    m->heading_cmd_deg = st->heading_deg;
}

void fm_clear_failsafe(flight_manager_t *m)
{
    /* Лінк ожив — знімаємо прапорець, але режим лишаємо автоматичним:
       керування повертає пілот тумблером, а не раптова поява пакета. */
    m->failsafe = false;
}

fm_output_t fm_step(flight_manager_t *m, const pilot_input_t *rc,
                    const vehicle_state_t *st, float dt)
{
    fm_output_t out;
    out.hint = HINT_NONE;
    float u = m->last_out;

    switch (m->mode) {
    case MODE_MANUAL:
        if (!rc->valid) {
            u = m->last_out;   /* лінк мовчить — тримаємо останнє до failsafe */
        } else if (m->stick_hold) {
            const float diff = rc->throttle - m->u_hold;
            if (rc->force_override || fabsf(diff) <= STICK_MATCH_WINDOW) {
                m->stick_hold = false;
                u = rc->throttle;
                out.hint = HINT_STICK_MATCHED;
            } else {
                u = m->u_hold;   /* віртуальний автотрим */
                out.hint = (diff < 0.0f) ? HINT_STICK_UP : HINT_STICK_DOWN;
            }
        } else {
            u = rc->throttle;
        }
        break;

    case MODE_ALT_HOLD:
        u = pid_update(&m->alt_pid, st->alt_m, st->climb_mps, dt);
        break;

    case MODE_AUTO_MISSION:
        u = pid_update(&m->mission_pid, st->alt_m, st->climb_mps, dt);
        break;
    }

    if (!isfinite(u)) u = m->last_out;

    /* Курс: у автоматі при failsafe розвертаємось на базу обмеженим темпом,
       поза failsafe тримаємо той, з яким увійшли. */
    if (m->mode == MODE_AUTO_MISSION) {
        const float target = m->failsafe ? m->home_bearing_deg : m->heading_cmd_deg;
        m->heading_cmd_deg = heading_step(m->heading_cmd_deg, target,
                                          YAW_RATE_MAX_DPS, dt);
    } else {
        m->heading_cmd_deg = st->heading_deg;
    }

    m->last_out = u;

    out.throttle = u;
    out.dshot_value = dshot_throttle_value(u, m->armed);
    out.dshot_packet = dshot_packet(out.dshot_value, false);
    out.heading_cmd_deg = m->heading_cmd_deg;
    return out;
}

const char *fm_mode_name(flight_mode_t mode)
{
    switch (mode) {
    case MODE_MANUAL:       return "MANUAL";
    case MODE_ALT_HOLD:     return "ALT_HOLD";
    case MODE_AUTO_MISSION: return "AUTO_MISSION";
    }
    return "?";
}

const char *fm_hint_text(stick_hint_t hint)
{
    switch (hint) {
    case HINT_NONE:          return "-";
    case HINT_STICK_UP:      return "ПІДНІМИ РУЧКУ";
    case HINT_STICK_DOWN:    return "ОПУСТИ РУЧКУ";
    case HINT_STICK_MATCHED: return "КЕРУВАННЯ ВІДДАНО";
    }
    return "?";
}

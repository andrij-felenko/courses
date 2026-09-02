#include "preflight.h"

static bool inside_fence(vec3_t p, const flight_envelope_t *env)
{
    if (p.x < env->min_x || p.x > env->max_x) {
        return false;
    }
    if (p.y < env->min_y || p.y > env->max_y) {
        return false;
    }
    /* NED: z росте вниз, тож висота над домом — це від'ємна різниця. */
    float altitude = -(p.z - env->home.z);
    if (altitude < 0.0f || altitude > env->max_altitude) {
        return false;
    }
    return true;
}

float preflight_leg_time(vec3_t from, vec3_t to, float airspeed, vec3_t wind)
{
    vec3_t d = vec3_sub(to, from);
    float dist = vec3_norm(d);
    if (dist < 0.01f) {
        return 0.0f; /* уже на місці */
    }
    if (airspeed < 0.1f) {
        return -1.0f;
    }

    vec3_t u = { d.x / dist, d.y / dist, d.z / dist };

    /* Трикутник швидкостей: розкладаємо вітер на складову вздовж треку
       (додається до колової швидкості) і поперечну (її доводиться
       компенсувати кутом випередження, і на це витрачається тяга). */
    float along = vec3_dot(wind, u);
    vec3_t cross = { wind.x - along * u.x,
                     wind.y - along * u.y,
                     wind.z - along * u.z };
    float cross_mag = vec3_norm(cross);

    if (cross_mag >= airspeed) {
        return -1.0f; /* знесе з треку: апарат просто не втримає лінію */
    }

    float ground = sqrtf(airspeed * airspeed - cross_mag * cross_mag) + along;
    if (ground < 0.1f) {
        return -1.0f; /* зустрічний вітер сильніший за апарат */
    }
    return dist / ground;
}

goal_check_t preflight_energy(const goal_t *g,
                              const system_state_t *sys,
                              const flight_envelope_t *env,
                              float *out_wh)
{
    float t_go = preflight_leg_time(sys->pos, g->target, g->cruise_airspeed, sys->wind);
    if (t_go < 0.0f) {
        return GOAL_CHECK_HEADWIND;
    }
    /* Другий відрізок — повернення з цільової точки додому. Саме він
       найчастіше й ріже ціль: туди за вітром швидко, назад проти вітру довго. */
    float t_back = preflight_leg_time(g->target, env->home, env->rth_airspeed, sys->wind);
    if (t_back < 0.0f) {
        return GOAL_CHECK_HEADWIND;
    }

    float wh = sys->cruise_power_w * (t_go + t_back) / 3600.0f * env->energy_reserve;
    if (out_wh != NULL) {
        *out_wh = wh;
    }
    if (wh > sys->battery_energy_wh) {
        return GOAL_CHECK_NO_ENERGY;
    }
    return GOAL_CHECK_OK;
}

goal_check_t preflight_check(const goal_t *g,
                             const system_state_t *sys,
                             const flight_envelope_t *env)
{
    if (g == NULL || sys == NULL || env == NULL) {
        return GOAL_CHECK_BAD_REQUEST;
    }
    if (g->cruise_airspeed < 0.1f || g->acceptance_radius <= 0.0f) {
        return GOAL_CHECK_BAD_REQUEST;
    }

    /* Аварійну ціль не фільтруємо: вона і є реакцією на те, що вже зламалося.
       Відмовити їй означає лишити апарат узагалі без плану дій. */
    if (g->priority == GOAL_PRIO_EMERGENCY) {
        return GOAL_CHECK_OK;
    }

    if (!sys->sensors_ok) {
        return GOAL_CHECK_SENSOR_FAILURE;
    }
    if (!sys->motors_ok) {
        return GOAL_CHECK_MOTOR_FAILURE;
    }
    if (sys->ekf_pos_variance > env->ekf_variance_limit) {
        return GOAL_CHECK_EKF_DIVERGED;
    }
    if (!inside_fence(g->target, env)) {
        return GOAL_CHECK_OUTSIDE_GEOFENCE;
    }
    if (sys->battery_voltage < env->rth_voltage) {
        return GOAL_CHECK_NO_ENERGY; /* просіла банка: нові місії вже не беремо */
    }

    return preflight_energy(g, sys, env, NULL);
}

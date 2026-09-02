#include "planner.h"

#include <math.h>

static float clearance(const Obstacle *obs, size_t n, float x, float y)
{
    float best = 1.0e6f;

    for (size_t i = 0; i < n; i++) {
        const float dx = x - obs[i].x;
        const float dy = y - obs[i].y;
        const float d  = sqrtf(dx * dx + dy * dy) - obs[i].radius;
        if (d < best) {
            best = d;
        }
    }
    return best;
}

/* Прогін однієї команди на горизонті T і накопичення вартості J. */
static float rollout_cost(const PlannerConfig *cfg, const SafetyLimits *lim,
                          Pose pose, Setpoint u,
                          const Obstacle *obs, size_t obs_n)
{
    const int steps = (int)(cfg->horizon_s / cfg->step_s);
    float x = pose.x, y = pose.y, th = pose.theta;
    float cost = 0.0f;

    for (int k = 0; k < steps; k++) {
        th += u.yaw_rate * cfg->step_s;
        x  += u.vx * cosf(th) * cfg->step_s;
        y  += u.vx * sinf(th) * cfg->step_s;

        const float c = clearance(obs, obs_n, x, y);
        if (c < lim->obstacle_margin_m) {
            return INFINITY; /* траєкторія неприпустима — не кандидат узагалі */
        }
        cost += cfg->w_risk / (c * c);
    }

    const float dx = cfg->goal_x - x;
    const float dy = cfg->goal_y - y;
    cost += cfg->w_goal * sqrtf(dx * dx + dy * dy);
    cost += cfg->w_effort * (0.05f * u.vx * u.vx + u.yaw_rate * u.yaw_rate);
    return cost;
}

Setpoint planner_solve(const PlannerConfig *cfg, const SafetyLimits *lim,
                       Pose pose, Setpoint current,
                       const Obstacle *obs, size_t obs_n, float *out_cost)
{
    const int   v_samples = 7;
    const int   w_samples = 13;
    const float dv = lim->accel_max * cfg->window_s;
    const float dw = lim->yaw_accel_max * cfg->window_s;

    float v_lo = current.vx - dv, v_hi = current.vx + dv;
    float w_lo = current.yaw_rate - dw, w_hi = current.yaw_rate + dw;

    if (v_lo < 0.0f)          v_lo = 0.0f;
    if (v_hi > lim->v_max)    v_hi = lim->v_max;
    if (w_lo < -lim->yaw_rate_max) w_lo = -lim->yaw_rate_max;
    if (w_hi > lim->yaw_rate_max)  w_hi = lim->yaw_rate_max;

    Setpoint best      = { 0.0f, 0.0f };
    float    best_cost = INFINITY;

    for (int i = 0; i < v_samples; i++) {
        const float v = v_lo + (v_hi - v_lo) * (float)i / (float)(v_samples - 1);
        for (int j = 0; j < w_samples; j++) {
            const float w = w_lo + (w_hi - w_lo) * (float)j / (float)(w_samples - 1);
            const Setpoint u = { v, w };
            const float cost = rollout_cost(cfg, lim, pose, u, obs, obs_n);
            if (cost < best_cost) {
                best_cost = cost;
                best = u;
            }
        }
    }

    *out_cost = best_cost;
    return best;
}

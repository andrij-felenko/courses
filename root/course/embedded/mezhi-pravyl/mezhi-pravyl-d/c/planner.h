#ifndef PLANNER_H
#define PLANNER_H

#include "rover.h"

/* Повільний контур: чисельний пошук уставки-кандидата на горизонті.
 * Оцінює інтегральний функціонал вартості J по вибірці допустимих команд;
 * може не знайти жодної придатної траєкторії — і це нормально, бо за
 * безпеку відповідає не він, а бар'єр. */

typedef struct {
    float x, y, theta;
} Pose;

typedef struct {
    float goal_x, goal_y;
    float w_goal;    /* вага наближення до цілі */
    float w_effort;  /* вага ||u||² */
    float w_risk;    /* вага близькості до перешкод */
    float horizon_s; /* горизонт прогнозу T */
    float step_s;    /* крок інтегрування */
    float window_s;  /* динамічне вікно: на скільки уставка може змінитись */
} PlannerConfig;

static inline PlannerConfig planner_default_config(float goal_x, float goal_y)
{
    PlannerConfig c = {
        .goal_x    = goal_x,
        .goal_y    = goal_y,
        .w_goal    = 1.0f,
        .w_effort  = 0.15f,
        .w_risk    = 0.05f,
        .horizon_s = 1.6f,
        .step_s    = 0.1f,
        .window_s  = 0.30f,
    };
    return c;
}

/* Повертає найкращого кандидата; *out_cost = INFINITY, якщо допустимої
 * траєкторії немає (тоді кандидата подавати не можна). */
Setpoint planner_solve(const PlannerConfig *cfg, const SafetyLimits *lim,
                       Pose pose, Setpoint current,
                       const Obstacle *obs, size_t obs_n, float *out_cost);

#endif /* PLANNER_H */

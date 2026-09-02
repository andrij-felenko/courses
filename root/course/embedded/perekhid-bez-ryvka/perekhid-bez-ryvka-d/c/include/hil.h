#ifndef HIL_H
#define HIL_H

#include <stdbool.h>

/* Три тести чеклиста валідації безривкового переходу на HIL-стенді. */

typedef struct {
    /* 1. Тест нульового стрибка */
    unsigned switch_count;
    float    glitch_worst;
    float    glitch_limit;
    bool     glitch_pass;

    /* 2. Тест насиченого передзавантаження */
    float    saturated_residual;      /* зрізана передзавантаженням частина */
    float    saturated_first_delta;   /* приріст виходу на першому такті */
    float    saturated_integral_drop; /* наскільки інтеграл зійшов з межі */
    bool     saturated_pass;

    /* 3. Тест темпу наростання */
    float    ramp_peak_setpoint_step;
    float    ramp_allowed_setpoint_step;
    float    ramp_peak_load_g;
    float    ramp_min_load_g;
    unsigned ramp_max_saturated_run;  /* найдовша серія тактів на упорі газу */
    bool     ramp_pass;
} hil_report_t;

void hil_run(hil_report_t *rep);
bool hil_all_passed(const hil_report_t *rep);

#endif /* HIL_H */

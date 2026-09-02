#ifndef NAV_GUARD_H
#define NAV_GUARD_H

#include <stdbool.h>

#include "flight_types.h"

/* Навігаційний контур утримання лінії шляху з двома захистами на час
   перехоплення: заморожуванням інтегратора й підтягуванням уставки. */

typedef struct {
    float leg_x, leg_y;     /* початок поточного відрізка */
    float wp_x, wp_y;       /* поворотний пункт маршруту */
    float alt_target;       /* м */
    float airspeed_target;  /* м/с */
} nav_setpoint_t;

typedef struct {
    nav_setpoint_t sp;

    float kp_xte, ki_xte, kd_xte; /* зовнішній контур: бічне відхилення → курс */
    float i_max;                  /* межа накопичення, градуси зносу */
    float decay_tau;              /* стала розвантаження інтегратора */
    float k_track;                /* внутрішній контур: похибка курсу → крен */
    float kp_alt, kp_spd, thr_trim;

    float integral;
    float prev_xte;
    bool  have_prev;
    bool  anti_windup;            /* вимикається лише для показу наслідків */
} nav_guard_t;

void  nav_guard_init(nav_guard_t *g, const nav_setpoint_t *sp);
float nav_guard_bearing(const nav_guard_t *g);
float nav_guard_crosstrack(const nav_guard_t *g, const vehicle_state_t *st);

/* frozen приходить із takeover_status_t.freeze_nav. */
control_command_t nav_guard_step(nav_guard_t *g,
                                 const vehicle_state_t *st,
                                 bool frozen,
                                 float dt_sec);

#endif /* NAV_GUARD_H */

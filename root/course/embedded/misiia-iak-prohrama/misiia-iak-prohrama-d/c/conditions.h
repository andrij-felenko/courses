#ifndef CONDITIONS_H
#define CONDITIONS_H

#include <stdbool.h>
#include <stdint.h>

#include "geo.h"

/* Допуск, за яким вважаємо розворот завершеним. */
#define COND_YAW_TOLERANCE_DEG 2.0f
/* Кутова швидкість за замовчуванням, коли param2 = 0. */
#define COND_YAW_DEFAULT_DPS   30.0f

typedef enum {
    COND_NONE = 0,
    COND_DELAY,     /* MAV_CMD_CONDITION_DELAY    (112) */
    COND_DISTANCE,  /* MAV_CMD_CONDITION_DISTANCE (114) */
    COND_YAW        /* MAV_CMD_CONDITION_YAW      (115) */
} cond_kind_t;

/* Активна умова. Живе в RAM і блокує ЛИШЕ чергу DO-команд:
   навігаційний контур весь цей час веде апарат далі. */
typedef struct {
    cond_kind_t kind;
    bool        armed;
    uint32_t    start_ms;
    uint32_t    duration_ms;    /* DELAY */
    float       trigger_dist_m; /* DISTANCE */
    float       target_yaw_deg; /* YAW */
    float       start_yaw_deg;  /* YAW */
    float       yaw_rate_dps;   /* YAW */
} condition_t;

/* Те, що умова бачить щотакту. */
typedef struct {
    uint32_t    now_ms;
    geo_point_t position;
    geo_point_t next_waypoint;   /* активна ціль навігаційного контуру */
    float       yaw_deg;
    float       battery_soc_pct;
} cond_ctx_t;

void  condition_arm(condition_t *c, cond_kind_t kind, float p1, float p2,
                    const cond_ctx_t *ctx);
bool  condition_met(const condition_t *c, const cond_ctx_t *ctx);

/* Проміжна уставка курсу для CONDITION_YAW: розворот ведеться
   із заданою кутовою швидкістю, а не стрибком на цільовий кут. */
float condition_yaw_setpoint(const condition_t *c, const cond_ctx_t *ctx);

/* Однополюсний НЧ-фільтр напруги акумулятора. Пряме читання напруги
   дає хибні спрацьовування: під ривком тяги вона просідає на
   внутрішньому опорі. Постійна часу 2–5 с гасить ці провали. */
typedef struct {
    float value_v;
    float tau_s;
    bool  primed;
} battery_filter_t;

void  battery_filter_init(battery_filter_t *f, float tau_s);
float battery_filter_update(battery_filter_t *f, float raw_v, float dt_s);

#endif /* CONDITIONS_H */

#ifndef TAKEOVER_H
#define TAKEOVER_H

#include <stdbool.h>
#include <stdint.h>

#include "flight_types.h"
#include "rc_input.h"

/* Автомат перехоплення керування: п'ять станів, коефіцієнт авторитету α
   та окремий авторитет по газу. */

#define TK_DEADBAND        0.12f  /* 12% ходу ручки — поріг перехоплення */
#define TK_BLEND_IN_SEC    0.20f  /* наростання авторитету пілота */
#define TK_BLEND_OUT_SEC   0.40f  /* повернення авторитету автоматові */
#define TK_HANDBACK_HOLD   1.50f  /* утримання нейтралі перед поверненням */
#define TK_THR_MOVE_RATE   0.20f  /* 1/с — швидкість важеля, яку вважаємо рухом */
#define TK_THR_RATE_TAU    0.10f  /* згладжування похідної газу */
#define TK_ACTIVE_EPS      0.02f  /* нижче цього α вважаємо нулем */
#define TK_EVENT_QUEUE     8u

typedef enum {
    TAKEOVER_AUTO_NAV = 0,
    TAKEOVER_OVERRIDE_IN,
    TAKEOVER_MANUAL_HOLD,
    TAKEOVER_HANDBACK_WAIT,
    TAKEOVER_BLENDING_OUT
} takeover_state_t;

typedef enum {
    TK_EVT_OVERRIDE_BEGIN = 0,
    TK_EVT_MANUAL_FULL,
    TK_EVT_HANDBACK_ARMED,
    TK_EVT_AUTO_RESUMED,
    TK_EVT_THROTTLE_ENGAGED,
    TK_EVT_RC_LOST,
    TK_EVT_FENCE_RECLAIM
} takeover_event_t;

typedef struct {
    takeover_state_t state;
    float alpha;          /* авторитет пілота по осях орієнтації */
    float alpha_throttle; /* авторитет пілота по газу */
    bool  freeze_nav;     /* заморозити інтегратори й підтягувати уставку */
    bool  request_rtl;    /* зв'язку немає — переходимо на аварійний план */
} takeover_status_t;

typedef struct {
    takeover_state_t state;
    float alpha;
    float alpha_thr;
    float hold_timer;
    float thr_prev;
    float thr_rate_lp;
    bool  thr_engaged;        /* важіль газу зрушив — газ теж під пілотом */
    bool  prev_switch_manual;
    bool  fence_latched;
    bool  rc_lost;
    bool  primed;             /* перший дійсний кадр уже бачили */
    takeover_event_t events[TK_EVENT_QUEUE];
    uint8_t evt_head;
    uint8_t evt_count;
} takeover_t;

void takeover_init(takeover_t *t);

takeover_status_t takeover_update(takeover_t *t,
                                  const rc_command_t *rc,
                                  bool fence_breach,
                                  float dt_sec);

control_command_t takeover_blend(const takeover_status_t *st,
                                 const control_command_t *cmd_auto,
                                 const control_command_t *cmd_pilot);

bool takeover_pop_event(takeover_t *t, takeover_event_t *out);

const char *takeover_state_name(takeover_state_t s);

#endif /* TAKEOVER_H */

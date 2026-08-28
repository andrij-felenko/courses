#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define STICK_FIGHT_THRESH    0.35f
#define FIGHT_TIME_LIMIT_MS   400
#define DEADZONE_THRESH       0.08f
#define DRIFT_SPEED_THRESH    1.5f     /* м/с */

typedef enum {
    MODE_STABILIZE = 0,
    MODE_ALT_HOLD,
    MODE_POS_HOLD,
    MODE_AUTO_RTH
} FlightMode;

typedef enum {
    CONSISTENCY_OK = 0,
    CONSISTENCY_WARN_MISMATCH,
    CONSISTENCY_TRIGGER_OVERRIDE
} ConsistencyStatus;

typedef struct {
    float roll;     /* [-1.0 .. 1.0] */
    float pitch;    /* [-1.0 .. 1.0] */
    float throttle; /* [0.0 .. 1.0] */
} RcSticks;

typedef struct {
    float vx;       /* North, м/с */
    float vy;       /* East, м/с */
} VelocityEstimate;

typedef struct {
    uint32_t fight_timer_ms;
    uint32_t drift_timer_ms;
    uint32_t last_cycle_time_ms;
    ConsistencyStatus status;
} ModeMonitorState;

void mode_monitor_init(ModeMonitorState *mon) {
    mon->fight_timer_ms = 0;
    mon->drift_timer_ms = 0;
    mon->last_cycle_time_ms = 0;
    mon->status = CONSISTENCY_OK;
}

ConsistencyStatus mode_monitor_eval(ModeMonitorState *mon,
                                   FlightMode mode,
                                   const RcSticks *rc,
                                   const VelocityEstimate *vel,
                                   uint32_t now_ms) {
    mon->status = CONSISTENCY_OK;

    /* 1. Виявлення боротьби зі стіками в автономному поверненні (RTH) */
    if (mode == MODE_AUTO_RTH) {
        float stick_mag = sqrtf(rc->roll * rc->roll + rc->pitch * rc->pitch);
        float vel_mag = sqrtf(vel->vx * vel->vx + vel->vy * vel->vy);

        if (stick_mag > STICK_FIGHT_THRESH && vel_mag > 0.5f) {
            /* Скалярний добуток: pitch вздовж vx, roll вздовж vy */
            float dot = (rc->pitch * vel->vx) + (rc->roll * vel->vy);
            if (dot < 0.0f) {
                if (mon->fight_timer_ms == 0) {
                    mon->fight_timer_ms = now_ms;
                } else if (now_ms - mon->fight_timer_ms > FIGHT_TIME_LIMIT_MS) {
                    mon->status = CONSISTENCY_TRIGGER_OVERRIDE;
                    return mon->status;
                }
            } else {
                mon->fight_timer_ms = 0;
            }
        } else {
            mon->fight_timer_ms = 0;
        }
    } else {
        mon->fight_timer_ms = 0;
    }

    /* 2. Виявлення дрейфу при очікуванні PosHold після непоміченого скидання в AltHold */
    if (mode == MODE_ALT_HOLD) {
        float stick_mag = sqrtf(rc->roll * rc->roll + rc->pitch * rc->pitch);
        float vel_mag = sqrtf(vel->vx * vel->vx + vel->vy * vel->vy);

        if (stick_mag < DEADZONE_THRESH && vel_mag > DRIFT_SPEED_THRESH) {
            if (mon->drift_timer_ms == 0) {
                mon->drift_timer_ms = now_ms;
            } else if (now_ms - mon->drift_timer_ms > 1000) {
                mon->status = CONSISTENCY_WARN_MISMATCH;
            }
        } else {
            mon->drift_timer_ms = 0;
        }
    } else {
        mon->drift_timer_ms = 0;
    }

    return mon->status;
}

#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define STICK_DEADZONE          0.08f
#define STICK_FIGHT_THRESHOLD   0.35f
#define THROTTLE_LOW_THRESHOLD  0.05f
#define DRIFT_SPEED_THRESHOLD   1.5f     /* м/с */
#define STIR_DERIVATIVE_THRESH  2.5f     /* 1/c */

#define FIGHTING_TIME_LIMIT_MS  400
#define THROTTLE_TIME_LIMIT_MS  800
#define DRIFT_TIME_LIMIT_MS     1200
#define STIR_WINDOW_MS          600
#define STIR_MAX_REVERSALS      4

typedef enum {
    FLIGHT_MODE_MANUAL = 0,
    FLIGHT_MODE_STABILIZE,
    FLIGHT_MODE_ALT_HOLD,
    FLIGHT_MODE_POS_HOLD,
    FLIGHT_MODE_AUTO_MISSION,
    FLIGHT_MODE_AUTO_RTH,
    FLIGHT_MODE_EMERGENCY_LAND
} FlightMode;

typedef enum {
    SEVERITY_NORMAL = 0,
    SEVERITY_WARNING_ANNUNCIATION,
    SEVERITY_OVERRIDE_TAKEOVER
} MismatchSeverity;

typedef struct {
    float roll;      /* Нормалізовані відхилення [-1.0 .. +1.0] */
    float pitch;
    float yaw;
    float throttle; /* [0.0 .. 1.0] */
} PilotSticks;

typedef struct {
    float vel_x;    /* Північ, м/с */
    float vel_y;    /* Схід, м/с */
    float vel_z;    /* Вниз, м/с */
} NavVector;

typedef struct {
    uint32_t fight_start_time_ms;
    uint32_t throttle_panic_start_ms;
    uint32_t drift_start_time_ms;
    
    float last_roll;
    float last_pitch;
    uint32_t last_update_ms;
    
    int reversal_count;
    uint32_t stir_window_start_ms;
    float last_sign;
    
    MismatchSeverity current_severity;
    const char *alarm_reason;
} ConsistencyMonitor;

void consistency_monitor_init(ConsistencyMonitor *mon) {
    mon->fight_start_time_ms = 0;
    mon->throttle_panic_start_ms = 0;
    mon->drift_start_time_ms = 0;
    mon->last_roll = 0.0f;
    mon->last_pitch = 0.0f;
    mon->last_update_ms = 0;
    mon->reversal_count = 0;
    mon->stir_window_start_ms = 0;
    mon->last_sign = 0.0f;
    mon->current_severity = SEVERITY_NORMAL;
    mon->alarm_reason = "OK";
}

MismatchSeverity consistency_monitor_update(ConsistencyMonitor *mon,
                                           FlightMode active_mode,
                                           const PilotSticks *sticks,
                                           const NavVector *nav,
                                           uint32_t now_ms) {
    float dt = (mon->last_update_ms == 0) ? 0.02f : (float)(now_ms - mon->last_update_ms) / 1000.0f;
    if (dt <= 0.0f) dt = 0.02f;
    mon->last_update_ms = now_ms;

    mon->current_severity = SEVERITY_NORMAL;
    mon->alarm_reason = "OK";

    /* 1. Перевірка на протидію автопілоту в автономних режимах */
    bool is_autonomous = (active_mode == FLIGHT_MODE_AUTO_MISSION || active_mode == FLIGHT_MODE_AUTO_RTH);
    if (is_autonomous) {
        float stick_mag = sqrtf(sticks->roll * sticks->roll + sticks->pitch * sticks->pitch);
        float nav_mag = sqrtf(nav->vel_x * nav->vel_x + nav->vel_y * nav->vel_y);

        if (stick_mag > STICK_FIGHT_THRESHOLD && nav_mag > 0.5f) {
            /* Скалярний добуток вектора стіка та вектора руху: roll -> vel_y (схід), pitch -> vel_x (північ) */
            float dot_product = (sticks->pitch * nav->vel_x) + (sticks->roll * nav->vel_y);
            if (dot_product < 0.0f) {
                if (mon->fight_start_time_ms == 0) {
                    mon->fight_start_time_ms = now_ms;
                } else if (now_ms - mon->fight_start_time_ms > FIGHTING_TIME_LIMIT_MS) {
                    mon->current_severity = SEVERITY_OVERRIDE_TAKEOVER;
                    mon->alarm_reason = "STICK_FIGHTING_RTH";
                    return mon->current_severity;
                }
            } else {
                mon->fight_start_time_ms = 0;
            }
        } else {
            mon->fight_start_time_ms = 0;
        }
    } else {
        mon->fight_start_time_ms = 0;
    }

    /* 2. Пастка нульового газу при утриманні висоти або поверненні */
    bool holds_altitude = (active_mode == FLIGHT_MODE_ALT_HOLD || 
                           active_mode == FLIGHT_MODE_POS_HOLD || 
                           is_autonomous);
    if (holds_altitude && sticks->throttle < THROTTLE_LOW_THRESHOLD) {
        if (mon->throttle_panic_start_ms == 0) {
            mon->throttle_panic_start_ms = now_ms;
        } else if (now_ms - mon->throttle_panic_start_ms > THROTTLE_TIME_LIMIT_MS) {
            mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
            mon->alarm_reason = "ZERO_THROTTLE_IN_ALTHOLD";
        }
    } else {
        mon->throttle_panic_start_ms = 0;
    }

    /* 3. Дрейф при очікуванні PosHold після відкату в AltHold */
    if (active_mode == FLIGHT_MODE_ALT_HOLD) {
        float stick_mag = sqrtf(sticks->roll * sticks->roll + sticks->pitch * sticks->pitch);
        float horiz_speed = sqrtf(nav->vel_x * nav->vel_x + nav->vel_y * nav->vel_y);

        if (stick_mag < STICK_DEADZONE && horiz_speed > DRIFT_SPEED_THRESHOLD) {
            if (mon->drift_start_time_ms == 0) {
                mon->drift_start_time_ms = now_ms;
            } else if (now_ms - mon->drift_start_time_ms > DRIFT_TIME_LIMIT_MS) {
                mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
                mon->alarm_reason = "UNNOTICED_DRIFT_IN_ALTHOLD";
            }
        } else {
            mon->drift_start_time_ms = 0;
        }
    } else {
        mon->drift_start_time_ms = 0;
    }

    /* 4. Виявлення панічного сіпання стіками */
    float d_roll = (sticks->roll - mon->last_roll) / dt;
    float current_sign = (d_roll > 0.1f) ? 1.0f : ((d_roll < -0.1f) ? -1.0f : 0.0f);

    if (now_ms - mon->stir_window_start_ms > STIR_WINDOW_MS) {
        mon->stir_window_start_ms = now_ms;
        mon->reversal_count = 0;
    }

    if (current_sign != 0.0f && mon->last_sign != 0.0f && current_sign != mon->last_sign) {
        if (fabsf(d_roll) > STIR_DERIVATIVE_THRESH) {
            mon->reversal_count++;
            if (mon->reversal_count >= STIR_MAX_REVERSALS) {
                mon->current_severity = SEVERITY_WARNING_ANNUNCIATION;
                mon->alarm_reason = "PANIC_STICK_STIRRING";
            }
        }
    }

    mon->last_sign = current_sign;
    mon->last_roll = sticks->roll;
    mon->last_pitch = sticks->pitch;

    return mon->current_severity;
}

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_RATE_DEG_S       360.0f
#define MAX_ANGLE_DEG        45.0f
#define SLEW_RATE_DEG_S      180.0f  // Максимальна швидкість зміни уставки при переході
#define RC_TIMEOUT_MS        500
#define OFFBOARD_TIMEOUT_MS  1000

typedef enum {
    MODE_DIRECT_MANUAL = 0, // 1. Acro / Rate: уставка кутової швидкості (град/с)
    MODE_ASSISTED_ANGLE,    // 2. Fly-by-Wire: уставка кута нахилу (град)
    MODE_SUPERVISORY_AUTO,  // 3. Наглядове: уставка від бортового комп'ютера
    MODE_FAILSAFE_LAND      // Аварійний спуск при відмові зв'язку
} control_mode_t;

typedef struct {
    float roll_deg;
    float pitch_deg;
    float yaw_deg;
    float rate_roll_deg_s;
    float rate_pitch_deg_s;
    float rate_yaw_deg_s;
} vehicle_state_t;

typedef struct {
    float roll_cmd;   // град/с (у Manual) або град (у Angle/Auto)
    float pitch_cmd;
    float yaw_cmd;
    float throttle;   // 0.0 .. 1.0
} control_setpoint_t;

typedef struct {
    control_mode_t current_mode;
    control_mode_t requested_mode;
    control_setpoint_t active_setpoint;
    control_setpoint_t target_setpoint;
    
    uint32_t last_rc_time_ms;
    uint32_t last_offboard_time_ms;
    bool is_transitioning;
    float transition_progress; // 0.0 .. 1.0
} mode_arbiter_t;

void mode_arbiter_init(mode_arbiter_t *arbiter) {
    arbiter->current_mode = MODE_ASSISTED_ANGLE;
    arbiter->requested_mode = MODE_ASSISTED_ANGLE;
    arbiter->active_setpoint = (control_setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arbiter->target_setpoint = (control_setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arbiter->last_rc_time_ms = 0;
    arbiter->last_offboard_time_ms = 0;
    arbiter->is_transitioning = false;
    arbiter->transition_progress = 1.0f;
}

static float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

static float apply_slew_rate(float current, float target, float max_delta) {
    float error = target - current;
    if (fabsf(error) <= max_delta) {
        return target;
    }
    return current + (error > 0.0f ? max_delta : -max_delta);
}

bool mode_arbiter_request_mode(mode_arbiter_t *arbiter, 
                               control_mode_t new_mode, 
                               const vehicle_state_t *state) {
    if (arbiter->current_mode == new_mode) {
        return true;
    }

    // БЕЗУДАРНИЙ ПЕРЕХІД: фіксація поточного стану як стартової точки нової уставки
    if (new_mode == MODE_DIRECT_MANUAL) {
        arbiter->active_setpoint.roll_cmd = state->rate_roll_deg_s;
        arbiter->active_setpoint.pitch_cmd = state->rate_pitch_deg_s;
        arbiter->active_setpoint.yaw_cmd = state->rate_yaw_deg_s;
    } else if (new_mode == MODE_ASSISTED_ANGLE || new_mode == MODE_SUPERVISORY_AUTO) {
        arbiter->active_setpoint.roll_cmd = clampf(state->roll_deg, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
        arbiter->active_setpoint.pitch_cmd = clampf(state->pitch_deg, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
        arbiter->active_setpoint.yaw_cmd = state->yaw_deg;
    }

    arbiter->current_mode = new_mode;
    arbiter->is_transitioning = true;
    arbiter->transition_progress = 0.0f;
    return true;
}

void mode_arbiter_update(mode_arbiter_t *arbiter,
                         const vehicle_state_t *state,
                         const control_setpoint_t *rc_sp,
                         const control_setpoint_t *offboard_sp,
                         uint32_t now_ms,
                         float dt_sec) {
    // 1. Моніторинг здоров'я лінків (Failsafe Watchdog)
    bool rc_valid = (now_ms - arbiter->last_rc_time_ms) <= RC_TIMEOUT_MS;
    bool offboard_valid = (now_ms - arbiter->last_offboard_time_ms) <= OFFBOARD_TIMEOUT_MS;

    // Сходинкова деградація при втраті зв'язку
    if (arbiter->current_mode == MODE_SUPERVISORY_AUTO && !offboard_valid) {
        if (rc_valid) {
            mode_arbiter_request_mode(arbiter, MODE_ASSISTED_ANGLE, state);
        } else {
            mode_arbiter_request_mode(arbiter, MODE_FAILSAFE_LAND, state);
        }
    } else if ((arbiter->current_mode == MODE_ASSISTED_ANGLE || 
                arbiter->current_mode == MODE_DIRECT_MANUAL) && !rc_valid) {
        mode_arbiter_request_mode(arbiter, MODE_FAILSAFE_LAND, state);
    }

    // 2. Селекція цільової уставки
    switch (arbiter->current_mode) {
        case MODE_DIRECT_MANUAL:
            arbiter->target_setpoint.roll_cmd = rc_sp->roll_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.pitch_cmd = rc_sp->pitch_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.yaw_cmd = rc_sp->yaw_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.throttle = rc_sp->throttle;
            break;

        case MODE_ASSISTED_ANGLE:
            arbiter->target_setpoint.roll_cmd = rc_sp->roll_cmd * MAX_ANGLE_DEG;
            arbiter->target_setpoint.pitch_cmd = rc_sp->pitch_cmd * MAX_ANGLE_DEG;
            arbiter->target_setpoint.yaw_cmd = rc_sp->yaw_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.throttle = rc_sp->throttle;
            break;

        case MODE_SUPERVISORY_AUTO:
            arbiter->target_setpoint.roll_cmd = clampf(offboard_sp->roll_cmd, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
            arbiter->target_setpoint.pitch_cmd = clampf(offboard_sp->pitch_cmd, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
            arbiter->target_setpoint.yaw_cmd = offboard_sp->yaw_cmd;
            arbiter->target_setpoint.throttle = offboard_sp->throttle;
            break;

        case MODE_FAILSAFE_LAND:
            arbiter->target_setpoint.roll_cmd = 0.0f;
            arbiter->target_setpoint.pitch_cmd = 0.0f;
            arbiter->target_setpoint.yaw_cmd = state->yaw_deg;
            arbiter->target_setpoint.throttle = 0.40f;
            break;
    }

    // 3. Фільтрація темпу наростання (Slew Rate)
    float max_delta = SLEW_RATE_DEG_S * dt_sec;
    arbiter->active_setpoint.roll_cmd = apply_slew_rate(arbiter->active_setpoint.roll_cmd, 
                                                         arbiter->target_setpoint.roll_cmd, 
                                                         max_delta);
    arbiter->active_setpoint.pitch_cmd = apply_slew_rate(arbiter->active_setpoint.pitch_cmd, 
                                                          arbiter->target_setpoint.pitch_cmd, 
                                                          max_delta);
    arbiter->active_setpoint.yaw_cmd = apply_slew_rate(arbiter->active_setpoint.yaw_cmd, 
                                                        arbiter->target_setpoint.yaw_cmd, 
                                                        max_delta);
    arbiter->active_setpoint.throttle = arbiter->target_setpoint.throttle;
}

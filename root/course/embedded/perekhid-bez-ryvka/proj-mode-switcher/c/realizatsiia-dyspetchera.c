#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    MODE_MANUAL = 0,
    MODE_ALT_HOLD,
    MODE_AUTO_MISSION
} flight_mode_t;

typedef struct {
    float kp, ki, kd, kff;
    float out_min, out_max;
    float i_min, i_max;
    float slew_rate_max;
} pid_cfg_t;

typedef struct {
    pid_cfg_t cfg;
    float integral;
    float prev_meas;
    float target_sp;
    float current_sp;
    float last_out;
    bool  ready;
} pid_t;

static inline float clamp(float v, float min_v, float max_v) {
    return (v < min_v) ? min_v : (v > max_v) ? max_v : v;
}

void pid_init(pid_t *p, const pid_cfg_t *c) {
    p->cfg = *c;
    p->integral = 0.0f;
    p->prev_meas = 0.0f;
    p->target_sp = 0.0f;
    p->current_sp = 0.0f;
    p->last_out = 0.0f;
    p->ready = false;
}

void pid_bumpless_handover(pid_t *p, float current_meas, float target_sp, float prev_out) {
    p->current_sp = current_meas;
    p->target_sp = target_sp;
    p->prev_meas = current_meas;

    float err = p->current_sp - current_meas; // 0
    float p_term = p->cfg.kp * err;
    float ff_term = p->cfg.kff * p->current_sp;

    float needed_i = prev_out - p_term - ff_term;
    p->integral = clamp(needed_i, p->cfg.i_min, p->cfg.i_max);
    p->last_out = prev_out;
    p->ready = true;
}

float pid_update(pid_t *p, float meas, float dt) {
    if (!p->ready || dt <= 0.0f) return p->last_out;

    // Ремпінг уставки
    if (p->cfg.slew_rate_max > 0.0f) {
        float max_step = p->cfg.slew_rate_max * dt;
        float d = p->target_sp - p->current_sp;
        if (d > max_step) p->current_sp += max_step;
        else if (d < -max_step) p->current_sp -= max_step;
        else p->current_sp = p->target_sp;
    } else {
        p->current_sp = p->target_sp;
    }

    float err = p->current_sp - meas;
    float p_term = p->cfg.kp * err;

    float d_meas = (meas - p->prev_meas) / dt;
    p->prev_meas = meas;
    float d_term = -p->cfg.kd * d_meas;

    float ff_term = p->cfg.kff * p->current_sp;
    float cand_i = p->integral + p->cfg.ki * err * dt;
    float u_raw = p_term + cand_i + d_term + ff_term;

    // Clamping анти-віндап
    bool sat_h = (u_raw > p->cfg.out_max) && (err > 0.0f);
    bool sat_l = (u_raw < p->cfg.out_min) && (err < 0.0f);
    if (!sat_h && !sat_l) {
        p->integral = clamp(cand_i, p->cfg.i_min, p->cfg.i_max);
    }

    p->last_out = clamp(u_raw, p->cfg.out_min, p->cfg.out_max);
    return p->last_out;
}

// ── Диспетчер режимів літака ──
typedef struct {
    flight_mode_t current_mode;
    pid_t alt_hold_pid;
    pid_t auto_mission_pid;
    float last_actuator_output;
} flight_manager_t;

void flight_manager_init(flight_manager_t *mgr) {
    mgr->current_mode = MODE_MANUAL;
    mgr->last_actuator_output = 0.0f;

    // Налаштування контуру утримання висоти
    pid_cfg_t alt_cfg = {
        .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 2.0f // набирати не більше 2 м/с
    };
    pid_init(&mgr->alt_hold_pid, &alt_cfg);

    // Налаштування контуру місії (агресивніший)
    pid_cfg_t auto_cfg = {
        .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 3.5f // набирати не більше 3.5 м/с
    };
    pid_init(&mgr->auto_mission_pid, &auto_cfg);
} 

void flight_manager_switch_mode(flight_manager_t *mgr, flight_mode_t new_mode,
                                float current_alt, float mission_target_alt) {
    if (new_mode == mgr->current_mode) return;

    float prev_out = mgr->last_actuator_output;

    switch (new_mode) {
        case MODE_MANUAL:
            // При поверненні в ручний режим привід віддається ручці пілота
            break;

        case MODE_ALT_HOLD:
            // Безривкове захоплення: поточна висота стає уставкою
            pid_bumpless_handover(&mgr->alt_hold_pid, current_alt, current_alt, prev_out);
            break;

        case MODE_AUTO_MISSION:
            // Безривкове захоплення: стартуємо з поточної висоти, але цілимося в точку місії
            pid_bumpless_handover(&mgr->auto_mission_pid, current_alt, mission_target_alt, prev_out);
            break;
    }

    mgr->current_mode = new_mode;
}

float flight_manager_step(flight_manager_t *mgr, float stick_throttle,
                          float current_alt, float dt) {
    float output = 0.0f;

    switch (mgr->current_mode) {
        case MODE_MANUAL:
            output = stick_throttle;
            break;

        case MODE_ALT_HOLD:
            output = pid_update(&mgr->alt_hold_pid, current_alt, dt);
            break;

        case MODE_AUTO_MISSION:
            output = pid_update(&mgr->auto_mission_pid, current_alt, dt);
            break;
    }

    mgr->last_actuator_output = output;
    return output;
}

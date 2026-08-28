#include "realtime_ml_controller.h"

void rt_triple_buffer_init(rt_triple_buffer_t *tb) {
    memset(tb->slots, 0, sizeof(tb->slots));
    atomic_init(&tb->clean_idx, 0);
    tb->write_idx = 1;
    tb->read_idx = 2;
}

void rt_triple_buffer_write(rt_triple_buffer_t *tb, const rt_ml_frame_t *frame) {
    memcpy(&tb->slots[tb->write_idx], frame, sizeof(rt_ml_frame_t));
    uint_fast8_t old_clean = atomic_exchange_explicit(&tb->clean_idx, tb->write_idx, memory_order_release);
    tb->write_idx = (uint8_t)old_clean;
}

bool rt_triple_buffer_read(rt_triple_buffer_t *tb, rt_ml_frame_t *out_frame) {
    uint_fast8_t current_clean = atomic_load_explicit(&tb->clean_idx, memory_order_acquire);
    if (current_clean != tb->read_idx) {
        uint_fast8_t old_clean = atomic_exchange_explicit(&tb->clean_idx, tb->read_idx, memory_order_acq_rel);
        tb->read_idx = (uint8_t)old_clean;
        memcpy(out_frame, &tb->slots[tb->read_idx], sizeof(rt_ml_frame_t));
        return true;
    }
    memcpy(out_frame, &tb->slots[tb->read_idx], sizeof(rt_ml_frame_t));
    return false;
}

void rt_ml_controller_init(rt_ml_controller_t *ctrl, const rt_watchdog_config_t *cfg) {
    ctrl->cfg = *cfg;
    memset(&ctrl->last_valid_frame, 0, sizeof(rt_ml_frame_t));
    memset(ctrl->last_derivatives, 0, sizeof(ctrl->last_derivatives));
    memset(ctrl->last_applied_output, 0, sizeof(ctrl->last_applied_output));
    ctrl->total_frames_received = 0;
    ctrl->deadline_miss_count = 0;
    ctrl->fallback_trigger_count = 0;
    ctrl->max_observed_latency_us = 0;
}

rt_ml_status_t rt_ml_controller_update(
    rt_ml_controller_t *ctrl,
    const rt_ml_frame_t *incoming_frame,
    bool is_fresh,
    uint64_t current_time_us,
    float out_correction[RT_ML_MAX_DIM])
{
    if (is_fresh) {
        ctrl->total_frames_received++;
        
        if (ctrl->last_valid_frame.timestamp_us > 0) {
            uint64_t latency = current_time_us - incoming_frame->timestamp_us;
            if (latency > ctrl->max_observed_latency_us) {
                ctrl->max_observed_latency_us = latency;
            }

            float dt_sec = (float)(incoming_frame->timestamp_us - ctrl->last_valid_frame.timestamp_us) * 1e-6f;
            if (dt_sec > 1e-4f) {
                for (int i = 0; i < RT_ML_MAX_DIM; ++i) {
                    ctrl->last_derivatives[i] = (incoming_frame->values[i] - ctrl->last_valid_frame.values[i]) / dt_sec;
                }
            }
        }
        ctrl->last_valid_frame = *incoming_frame;
    }

    if (ctrl->last_valid_frame.timestamp_us == 0) {
        memset(out_correction, 0, sizeof(float) * RT_ML_MAX_DIM);
        return RT_ML_STATUS_FALLBACK_PID;
    }

    uint64_t age_us = current_time_us - ctrl->last_valid_frame.timestamp_us;

    /* Режим 1: Свіжі дані */
    if (age_us <= ctrl->cfg.deadline_limit_us) {
        for (int i = 0; i < RT_ML_MAX_DIM; ++i) {
            out_correction[i] = ctrl->last_valid_frame.values[i];
            ctrl->last_applied_output[i] = out_correction[i];
        }
        return RT_ML_STATUS_FRESH;
    }

    ctrl->deadline_miss_count++;

    /* Режим 2: Екстраполяція */
    if (age_us <= ctrl->cfg.max_extrap_us) {
        float dt_extrap = (float)(age_us - ctrl->cfg.deadline_limit_us) * 1e-6f;
        float decay = expf(-ctrl->cfg.decay_lambda * dt_extrap);

        for (int i = 0; i < RT_ML_MAX_DIM; ++i) {
            float raw_extrap = ctrl->last_valid_frame.values[i] + ctrl->last_derivatives[i] * dt_extrap;
            out_correction[i] = raw_extrap * decay;
            ctrl->last_applied_output[i] = out_correction[i];
        }
        return RT_ML_STATUS_EXTRAPOLATED;
    }

    ctrl->fallback_trigger_count++;

    /* Режим 3: Перехід на Fallback */
    if (age_us <= ctrl->cfg.fatal_timeout_us) {
        memset(out_correction, 0, sizeof(float) * RT_ML_MAX_DIM);
        return RT_ML_STATUS_FALLBACK_PID;
    }

    /* Режим 4: Аварійна зупинка */
    memset(out_correction, 0, sizeof(float) * RT_ML_MAX_DIM);
    return RT_ML_STATUS_EMERGENCY_STOP;
}

void rt_fallback_pid_init(rt_fallback_pid_t *pid, float kp, float ki, float kd, float ts, float min_val, float max_val) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->ts_sec = ts;
    pid->out_min = min_val;
    pid->out_max = max_val;
    pid->integral_accum = 0.0f;
    pid->prev_error = 0.0f;
}

float rt_fallback_pid_step(rt_fallback_pid_t *pid, float setpoint, float feedback, float external_active_u, bool is_fallback_active) {
    float error = setpoint - feedback;
    float p_term = pid->kp * error;
    float d_term = (pid->ts_sec > 1e-6f) ? (pid->kd * (error - pid->prev_error) / pid->ts_sec) : 0.0f;
    pid->prev_error = error;

    if (!is_fallback_active) {
        /* Режим гарячого стеження (Bumpless Transfer): узгоджуємо інтегратор із зовнішнім ML-виходом */
        if (fabsf(pid->ki) > 1e-6f) {
            pid->integral_accum = (external_active_u - p_term - d_term) / pid->ki;
        }
        return external_active_u;
    }

    /* Активний режим Fallback: стандартне інтегрування з Anti-Windup */
    pid->integral_accum += error * pid->ts_sec;
    float i_term = pid->ki * pid->integral_accum;
    float raw_u = p_term + i_term + d_term;

    /* Насичення виходу */
    if (raw_u > pid->out_max) {
        raw_u = pid->out_max;
        /* Anti-Windup Clamping */
        if (error > 0.0f) {
            pid->integral_accum -= error * pid->ts_sec;
        }
    } else if (raw_u < pid->out_min) {
        raw_u = pid->out_min;
        if (error < 0.0f) {
            pid->integral_accum -= error * pid->ts_sec;
        }
    }

    return raw_u;
}

/* docking_controller.c */
#include "docking_controller.h"
#include <string.h>

void docking_kalman_init(docking_kalman_filter_t *kf, float q_pos, float q_vel, float r_pos) {
    if (!kf) return;
    memset(kf, 0, sizeof(docking_kalman_filter_t));
    kf->q_pos = q_pos;
    kf->q_vel = q_vel;
    kf->r_pos = r_pos;

    for (int i = 0; i < 6; ++i) {
        kf->P[i][i] = 1.0f;
    }
    kf->initialized = false;
}

void docking_kalman_predict(docking_kalman_filter_t *kf, float dt) {
    if (!kf || !kf->initialized || dt <= 0.0f) return;

    /* x = F * x */
    for (int i = 0; i < 3; ++i) {
        kf->x[i] += kf->x[i + 3] * dt;
    }

    /* P = F * P * F^T + Q */
    for (int i = 0; i < 3; ++i) {
        kf->P[i][i] += (kf->P[i + 3][i + 3] * dt * dt) + (2.0f * kf->P[i][i + 3] * dt) + (kf->q_pos * dt);
        kf->P[i][i + 3] += kf->P[i + 3][i + 3] * dt;
        kf->P[i + 3][i] = kf->P[i][i + 3];
        kf->P[i + 3][i + 3] += kf->q_vel * dt;
    }
}

void docking_kalman_update(docking_kalman_filter_t *kf, const float meas_pos[3]) {
    if (!kf || !meas_pos) return;

    if (!kf->initialized) {
        for (int i = 0; i < 3; ++i) {
            kf->x[i] = meas_pos[i];
            kf->x[i + 3] = 0.0f;
        }
        kf->initialized = true;
        return;
    }

    for (int i = 0; i < 3; ++i) {
        float y = meas_pos[i] - kf->x[i];
        float s = kf->P[i][i] + kf->r_pos;
        if (fabsf(s) > 1e-6f) {
            float k_gain = kf->P[i][i] / s;
            float k_gain_vel = kf->P[i + 3][i] / s;

            kf->x[i] += k_gain * y;
            kf->x[i + 3] += k_gain_vel * y;

            kf->P[i][i] *= (1.0f - k_gain);
            kf->P[i + 3][i + 3] -= k_gain_vel * kf->P[i][i + 3];
            kf->P[i][i + 3] *= (1.0f - k_gain);
            kf->P[i + 3][i] = kf->P[i][i + 3];
        }
    }
}

bool docking_solve_pnp(const camera_intrinsics_t *cam, const fiducial_corners_t *corners, float out_pos_body[3], float *out_yaw_rad) {
    if (!cam || !corners || !out_pos_body || !out_yaw_rad || !corners->valid) {
        return false;
    }

    /* Спрощений аналітичний розв'язок для плаского маркера з відомим розміром */
    float du1 = corners->u[1] - corners->u[0];
    float dv1 = corners->v[1] - corners->v[0];
    float pixel_width = sqrtf(du1 * du1 + dv1 * dv1);

    if (pixel_width < 4.0f) return false;

    float z_cam = (cam->fx * cam->tag_size_m) / pixel_width;
    float u_center = (corners->u[0] + corners->u[1] + corners->u[2] + corners->u[3]) * 0.25f;
    float v_center = (corners->v[0] + corners->v[1] + corners->v[2] + corners->v[3]) * 0.25f;

    float x_cam = (u_center - cam->cx) * z_cam / cam->fx;
    float y_cam = (v_center - cam->cy) * z_cam / cam->fy;

    /* Перехід у Body Frame NED: X_body = Y_cam, Y_body = X_cam, Z_body = Z_cam */
    out_pos_body[0] = y_cam;
    out_pos_body[1] = x_cam;
    out_pos_body[2] = z_cam;

    *out_yaw_rad = atan2f(dv1, du1);
    return true;
}

void docking_guidance_compute(
    const docking_target_state_t *target,
    const guidance_params_t *params,
    float dt,
    guidance_output_t *out)
{
    if (!target || !params || !out) return;

    memset(out, 0, sizeof(guidance_output_t));

    if (!target->is_tracking) {
        out->vel_cmd_body[0] = 0.0f;
        out->vel_cmd_body[1] = 0.0f;
        out->vel_cmd_body[2] = 0.0f;
        return;
    }

    float ex = target->pos_body[0];
    float ey = target->pos_body[1];
    float ez = target->pos_body[2];

    /* Горизонтальний ПД-регулятор */
    float vx = params->kp_xy * ex - params->kd_xy * target->vel_body[0];
    float vy = params->kp_xy * ey - params->kd_xy * target->vel_body[1];

    /* Насичення горизонтальної швидкості */
    float h_speed = sqrtf(vx * vx + vy * vy);
    if (h_speed > params->max_horiz_vel) {
        vx = (vx / h_speed) * params->max_horiz_vel;
        vy = (vy / h_speed) * params->max_horiz_vel;
    }

    /* Вертикальний профіль спуску */
    float vz = params->kz_desc * ez;
    if (vz > params->max_desc_vel) vz = params->max_desc_vel;
    if (vz < params->min_desc_vel) vz = params->min_desc_vel;

    /* Фінальний етап посадки */
    if (ez < params->land_height_threshold) {
        vx = 0.0f;
        vy = 0.0f;
        vz = params->min_desc_vel;
        out->initiate_touchdown = true;
    }

    out->vel_cmd_body[0] = vx;
    out->vel_cmd_body[1] = vy;
    out->vel_cmd_body[2] = vz;
    out->yaw_rate_cmd_rad = -0.8f * target->yaw_relative_rad;
}

void dock_station_fsm_init(dock_station_controller_t *ctrl) {
    if (!ctrl) return;
    ctrl->state = DOCK_STATE_IDLE;
    ctrl->state_timer_ms = 0;
    ctrl->contact_resistance_mohm = 0.0f;
    ctrl->retry_count = 0;
}

void dock_station_fsm_update(
    dock_station_controller_t *ctrl,
    const dock_hardware_inputs_t *inputs,
    dock_hardware_outputs_t *outputs,
    uint32_t dt_ms)
{
    if (!ctrl || !inputs || !outputs) return;

    ctrl->state_timer_ms += dt_ms;

    if (inputs->emergency_stop_pressed) {
        ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
    }

    switch (ctrl->state) {
    case DOCK_STATE_IDLE:
        outputs->roof_open_cmd = false;
        outputs->clamp_motors_engage = false;
        outputs->probe_generator_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->main_power_relay_enable = false;
        outputs->cooling_fans_enable = false;
        break;

    case DOCK_STATE_ROOF_OPENING:
        outputs->roof_open_cmd = true;
        if (ctrl->state_timer_ms > 4000) {
            ctrl->state = DOCK_STATE_WAITING_UAV_APPROACH;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_WAITING_UAV_APPROACH:
        outputs->roof_open_cmd = true;
        if (inputs->uav_disarmed) {
            ctrl->state = DOCK_STATE_TOUCHDOWN_CONFIRMED;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_TOUCHDOWN_CONFIRMED:
        /* Затримка на повну зупинку пропелерів */
        if (ctrl->state_timer_ms > 2000) {
            ctrl->state = DOCK_STATE_MECHANICAL_CLAMPING;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_MECHANICAL_CLAMPING:
        outputs->clamp_motors_engage = true;
        if (ctrl->state_timer_ms > 3500) {
            ctrl->state = DOCK_STATE_CONTACT_PROBE;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_CONTACT_PROBE:
        outputs->probe_generator_enable = true;
        if (inputs->probe_current_ma > 50.0f) {
            ctrl->contact_resistance_mohm = (inputs->sense_voltage_drop_mv / inputs->probe_current_ma) * 1000.0f;
            if (ctrl->contact_resistance_mohm < 40.0f && inputs->bms_can_alive) {
                ctrl->state = DOCK_STATE_PRECHARGE_SOFTSTART;
                ctrl->state_timer_ms = 0;
            } else if (ctrl->state_timer_ms > 2000) {
                /* Спроба повторного затискання при високому опорі */
                if (ctrl->retry_count++ < 3) {
                    ctrl->state = DOCK_STATE_MECHANICAL_CLAMPING;
                } else {
                    ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
                }
                ctrl->state_timer_ms = 0;
            }
        }
        break;

    case DOCK_STATE_PRECHARGE_SOFTSTART:
        outputs->probe_generator_enable = false;
        outputs->precharge_relay_enable = true;
        outputs->target_psu_voltage_v = 25.2f;
        outputs->target_psu_current_limit_a = 2.0f;

        if (ctrl->state_timer_ms > 150) {
            ctrl->state = DOCK_STATE_MAIN_CHARGING;
            ctrl->state_timer_ms = 0;
        }
        break;

    case DOCK_STATE_MAIN_CHARGING:
        outputs->precharge_relay_enable = true;
        outputs->main_power_relay_enable = true;
        outputs->cooling_fans_enable = true;
        outputs->target_psu_voltage_v = 25.2f;
        outputs->target_psu_current_limit_a = 15.0f;

        /* Перевірка критичної температури комірок */
        for (uint8_t i = 0; i < inputs->cell_count; ++i) {
            if (inputs->cell_temperatures_c[i] > 48.0f) {
                ctrl->state = DOCK_STATE_EMERGENCY_ISOLATION;
                break;
            }
        }

        /* Критерій завершення заряду (CV стадія зі спадом струму) */
        if (inputs->battery_voltage_mv >= 25150 && inputs->charge_current_a < 0.5f) {
            if (ctrl->state_timer_ms > 5000) {
                ctrl->state = DOCK_STATE_CHARGE_COMPLETE;
                ctrl->state_timer_ms = 0;
            }
        }
        break;

    case DOCK_STATE_CHARGE_COMPLETE:
        outputs->main_power_relay_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->cooling_fans_enable = false;
        break;

    case DOCK_STATE_EMERGENCY_ISOLATION:
    default:
        outputs->main_power_relay_enable = false;
        outputs->precharge_relay_enable = false;
        outputs->probe_generator_enable = false;
        outputs->cooling_fans_enable = false;
        outputs->clamp_motors_engage = false;
        break;
    }
}

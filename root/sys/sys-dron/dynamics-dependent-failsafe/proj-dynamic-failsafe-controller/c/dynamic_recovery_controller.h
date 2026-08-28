/* dynamic_recovery_controller.h */
#ifndef DYNAMIC_RECOVERY_CONTROLLER_H
#define DYNAMIC_RECOVERY_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CLAMP(val, lo, hi) (((val) < (lo)) ? (lo) : (((val) > (hi)) ? (hi) : (val)))

typedef enum {
    RECOVERY_STATE_IDLE = 0,
    RECOVERY_STATE_RATE_DAMPING,   /* Фаза 0: демпфування обертання */
    RECOVERY_STATE_UNROLL,         /* Фаза 1: зняття крену (Roll-First) */
    RECOVERY_STATE_G_PULLOUT,      /* Фаза 2: вивід з пікірування з лімітом nz */
    RECOVERY_STATE_ENERGY_CLIMB,   /* Фаза 3: стабілізація швидкості та набір */
    RECOVERY_STATE_HANDOFF         /* Фаза 4: передача в штатний RTL */
} recovery_state_t;

typedef struct {
    float q_w;                     /* Кватерніон орієнтації w */
    float q_x;                     /* Кватерніон орієнтації x */
    float q_y;                     /* Кватерніон орієнтації y */
    float q_z;                     /* Кватерніон орієнтації z */
    float gyro_p_rad_s;            /* Кутова швидкість крену [рад/с] */
    float gyro_q_rad_s;            /* Кутова швидкість тангажу [рад/с] */
    float gyro_r_rad_s;            /* Кутова швидкість рискання [рад/с] */
    float accel_x_m_s2;            /* Поздовжнє прискорення [м/с²] */
    float accel_y_m_s2;            /* Бокове прискорення [м/с²] */
    float accel_z_m_s2;            /* Нормальне прискорення [м/с²] */
    float airspeed_ias_m_s;        /* Приладова швидкість [м/с] */
    float altitude_rel_m;          /* Відносна висота [м] */
    float climb_rate_m_s;          /* Вертикальна швидкість (+ вгору) [м/с] */
} recovery_input_state_t;

typedef struct {
    float max_allowed_nz;          /* Ліміт перевантаження (2.5) */
    float stall_speed_m_s;         /* Швидкість звалювання (13.0 м/с) */
    float cruise_speed_m_s;        /* Крейсерська швидкість (22.0 м/с) */
    float vne_speed_m_s;           /* Максимальна швидкість V_NE (45.0 м/с) */
    float safe_recovery_alt_m;     /* Безпечна висота передачі (50.0 м) */
    float v_ref_tuning_m_s;        /* Швидкість налаштування ПІД (20.0 м/с) */
} recovery_config_t;

typedef struct {
    float aileron;                 /* Елерони [-1.0 .. +1.0] */
    float elevator;                /* Руль висоти [-1.0 .. +1.0] */
    float rudder;                  /* Руль напрямку [-1.0 .. +1.0] */
    float throttle;                /* Дросель [0.0 .. 1.0] */
    recovery_state_t state;        /* Поточний стан */
    bool ready_for_navigation;     /* Готовність до повернення в RTL */
} recovery_actuator_cmd_t;

typedef struct {
    recovery_state_t state;
    recovery_config_t cfg;
    float nz_integrator;
    float state_timer_s;
} recovery_controller_t;

static inline void quat_to_euler_angles(float qw, float qx, float qy, float qz,
                                        float *roll, float *pitch, float *yaw) {
    float sinr_cosp = 2.0f * (qw * qx + qy * qz);
    float cosr_cosp = 1.0f - 2.0f * (qx * qx + qy * qy);
    *roll = atan2f(sinr_cosp, cosr_cosp);

    float sinp = 2.0f * (qw * qy - qz * qx);
    if (fabsf(sinp) >= 1.0f) {
        *pitch = copysignf(1.57079632679f, sinp);
    } else {
        *pitch = asinf(sinp);
    }

    float siny_cosp = 2.0f * (qw * qz + qx * qy);
    float cosy_cosp = 1.0f - 2.0f * (qy * qy + qz * qz);
    *yaw = atan2f(siny_cosp, cosy_cosp);
}

void recovery_controller_init(recovery_controller_t *ctrl, const recovery_config_t *cfg) {
    ctrl->state = RECOVERY_STATE_IDLE;
    ctrl->cfg = *cfg;
    ctrl->nz_integrator = 0.0f;
    ctrl->state_timer_s = 0.0f;
}

void recovery_controller_trigger(recovery_controller_t *ctrl) {
    if (ctrl->state == RECOVERY_STATE_IDLE) {
        ctrl->state = RECOVERY_STATE_RATE_DAMPING;
        ctrl->nz_integrator = 0.0f;
        ctrl->state_timer_s = 0.0f;
    }
}

void recovery_controller_reset(recovery_controller_t *ctrl) {
    ctrl->state = RECOVERY_STATE_IDLE;
    ctrl->nz_integrator = 0.0f;
    ctrl->state_timer_s = 0.0f;
}

recovery_actuator_cmd_t recovery_controller_update(recovery_controller_t *ctrl,
                                                  const recovery_input_state_t *st,
                                                  float dt) {
    recovery_actuator_cmd_t cmd = {0};
    cmd.state = ctrl->state;

    if (ctrl->state == RECOVERY_STATE_IDLE) {
        return cmd;
    }

    ctrl->state_timer_s += dt;

    float roll, pitch, yaw;
    quat_to_euler_angles(st->q_w, st->q_x, st->q_y, st->q_z, &roll, &pitch, &yaw);

    /* Масштабування за динамічним тиском */
    float v_safe = (st->airspeed_ias_m_s > 6.0f) ? st->airspeed_ias_m_s : 6.0f;
    float q_ratio = (ctrl->cfg.v_ref_tuning_m_s * ctrl->cfg.v_ref_tuning_m_s) / (v_safe * v_safe);
    float q_scale = CLAMP(q_ratio, 0.25f, 2.50f);

    /* Перевантаження nz */
    const float g_const = 9.80665f;
    float nz_current = 1.0f - (st->accel_z_m_s2 / g_const);

    switch (ctrl->state) {
    case RECOVERY_STATE_RATE_DAMPING: {
        cmd.aileron = (-st->gyro_p_rad_s * 0.35f) * q_scale;
        cmd.elevator = (-st->gyro_q_rad_s * 0.25f) * q_scale;
        cmd.rudder = (-st->gyro_r_rad_s * 0.30f) * q_scale;
        cmd.throttle = (st->airspeed_ias_m_s > ctrl->cfg.cruise_speed_m_s) ? 0.05f : 0.35f;

        bool rates_damped = (fabsf(st->gyro_p_rad_s) < 0.60f &&
                             fabsf(st->gyro_q_rad_s) < 0.60f &&
                             fabsf(st->gyro_r_rad_s) < 0.60f);

        if (rates_damped || ctrl->state_timer_s > 0.6f) {
            ctrl->state = RECOVERY_STATE_UNROLL;
            ctrl->state_timer_s = 0.0f;
        }
        break;
    }

    case RECOVERY_STATE_UNROLL: {
        float roll_error = 0.0f - roll;
        cmd.aileron = (roll_error * 1.70f - st->gyro_p_rad_s * 0.22f) * q_scale;
        cmd.elevator = (-st->gyro_q_rad_s * 0.15f) * q_scale;
        cmd.rudder = (-st->gyro_r_rad_s * 0.25f) * q_scale;
        cmd.throttle = (st->airspeed_ias_m_s > ctrl->cfg.cruise_speed_m_s) ? 0.05f : 0.40f;

        if (fabsf(roll) < 0.26f && fabsf(st->gyro_p_rad_s) < 0.30f) {
            ctrl->state = RECOVERY_STATE_G_PULLOUT;
            ctrl->state_timer_s = 0.0f;
            ctrl->nz_integrator = 0.0f;
        }
        break;
    }

    case RECOVERY_STATE_G_PULLOUT: {
        cmd.aileron = (0.0f - roll) * 1.30f * q_scale;
        cmd.rudder = (-st->gyro_r_rad_s * 0.20f) * q_scale;

        float target_nz = (ctrl->cfg.max_allowed_nz < 2.5f) ? ctrl->cfg.max_allowed_nz : 2.5f;
        float nz_err = target_nz - nz_current;
        ctrl->nz_integrator += nz_err * dt * 0.45f;
        ctrl->nz_integrator = CLAMP(ctrl->nz_integrator, -0.25f, 0.45f);

        float elev_demand = nz_err * 0.32f + ctrl->nz_integrator - st->gyro_q_rad_s * 0.18f;
        cmd.elevator = elev_demand * q_scale;
        cmd.throttle = (st->airspeed_ias_m_s > ctrl->cfg.cruise_speed_m_s) ? 0.0f : 0.50f;

        if (pitch >= -0.05f && st->climb_rate_m_s >= -0.5f) {
            ctrl->state = RECOVERY_STATE_ENERGY_CLIMB;
            ctrl->state_timer_s = 0.0f;
        }
        break;
    }

    case RECOVERY_STATE_ENERGY_CLIMB: {
        cmd.aileron = (0.0f - roll) * 1.10f * q_scale;
        cmd.rudder = (-st->gyro_r_rad_s * 0.20f) * q_scale;

        float target_pitch = 0.12f;
        if (st->airspeed_ias_m_s < ctrl->cfg.stall_speed_m_s * 1.30f) {
            target_pitch = 0.02f;
        }

        float pitch_err = target_pitch - pitch;
        cmd.elevator = (pitch_err * 1.35f - st->gyro_q_rad_s * 0.20f) * q_scale;
        cmd.throttle = 0.85f;

        if (st->altitude_rel_m >= ctrl->cfg.safe_recovery_alt_m &&
            st->airspeed_ias_m_s >= ctrl->cfg.stall_speed_m_s * 1.35f) {
            ctrl->state = RECOVERY_STATE_HANDOFF;
            ctrl->state_timer_s = 0.0f;
        }
        break;
    }

    case RECOVERY_STATE_HANDOFF: {
        cmd.aileron = (0.0f - roll) * 1.0f * q_scale;
        cmd.elevator = (0.03f - pitch) * 1.0f * q_scale;
        cmd.rudder = (-st->gyro_r_rad_s * 0.20f) * q_scale;
        cmd.throttle = 0.60f;
        cmd.ready_for_navigation = true;
        break;
    }

    case RECOVERY_STATE_IDLE:
        break;
    }

    cmd.aileron = CLAMP(cmd.aileron, -1.0f, 1.0f);
    cmd.elevator = CLAMP(cmd.elevator, -1.0f, 1.0f);
    cmd.rudder = CLAMP(cmd.rudder, -1.0f, 1.0f);
    cmd.throttle = CLAMP(cmd.throttle, 0.0f, 1.0f);

    return cmd;
}

/* dynamic_failsafe_core.h */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CLAMP(val, lo, hi) (((val) < (lo)) ? (lo) : (((val) > (hi)) ? (hi) : (val)))

typedef enum {
    FAILSAFE_PHASE_IDLE = 0,
    FAILSAFE_PHASE_UNROLL,      /* Фаза 1: гасіння кутових швидкостей та крену */
    FAILSAFE_PHASE_PULLOUT,     /* Фаза 2: вивід з пікірування з лімітом G */
    FAILSAFE_PHASE_ENERGY_CLIMB,/* Фаза 3: стабілізація швидкості та набір висоти */
    FAILSAFE_PHASE_HANDOFF      /* Фаза 4: передача в навігаційний RTL */
} failsafe_phase_t;

typedef struct {
    float roll_rad;          /* Крен [рад] */
    float pitch_rad;         /* Тангаж [рад] */
    float gyro_p;            /* Швидкість крену [рад/с] */
    float gyro_q;            /* Швидкість тангажу [рад/с] */
    float gyro_r;            /* Швидкість рискання [рад/с] */
    float airspeed_m_s;      /* Приладова швидкість [м/с] */
    float accel_z_m_s2;      /* Прискорення по осі Z [м/с²] */
    float altitude_m;        /* Висота [м] */
    float vz_m_s;            /* Вертикальна швидкість (+ вгору) [м/с] */
} vehicle_state_t;

typedef struct {
    float max_nz;            /* Граничне перевантаження (напр. 2.5g) */
    float stall_airspeed;    /* Швидкість звалювання (напр. 13.0 м/с) */
    float cruise_airspeed;   /* Крейсерська швидкість (напр. 22.0 м/с) */
    float safe_altitude;     /* Безпечна висота переходу (напр. 60.0 м) */
    float v_ref_airspeed;    /* Швидкість налаштування ПІД (20.0 м/с) */
} failsafe_config_t;

typedef struct {
    float aileron_cmd;       /* Елерони [-1.0 .. +1.0] */
    float elevator_cmd;      /* Руль висоти [-1.0 .. +1.0] */
    float rudder_cmd;        /* Руль напрямку [-1.0 .. +1.0] */
    float throttle_cmd;      /* Дросель [0.0 .. 1.0] */
    failsafe_phase_t phase;  /* Поточна фаза */
    bool ready_for_rtl;      /* Прапорець завершення маневру */
} failsafe_output_t;

typedef struct {
    failsafe_phase_t phase;
    failsafe_config_t cfg;
    float nz_integral;
} failsafe_controller_t;

void failsafe_init(failsafe_controller_t *ctrl, const failsafe_config_t *cfg) {
    ctrl->phase = FAILSAFE_PHASE_IDLE;
    ctrl->cfg = *cfg;
    ctrl->nz_integral = 0.0f;
}

void failsafe_trigger(failsafe_controller_t *ctrl) {
    if (ctrl->phase == FAILSAFE_PHASE_IDLE) {
        ctrl->phase = FAILSAFE_PHASE_UNROLL;
        ctrl->nz_integral = 0.0f;
    }
}

failsafe_output_t failsafe_update(failsafe_controller_t *ctrl, const vehicle_state_t *st, float dt) {
    failsafe_output_t out = {0};
    out.phase = ctrl->phase;

    if (ctrl->phase == FAILSAFE_PHASE_IDLE) {
        return out;
    }

    /* 1. Розрахунок Q-scheduling */
    float v_curr = (st->airspeed_m_s > 5.0f) ? st->airspeed_m_s : 5.0f;
    float q_scale = (ctrl->cfg.v_ref_airspeed * ctrl->cfg.v_ref_airspeed) / (v_curr * v_curr);
    q_scale = CLAMP(q_scale, 0.25f, 2.50f);

    /* 2. Поточне перевантаження nz = 1 - az / 9.81 */
    float nz_current = 1.0f - (st->accel_z_m_s2 / 9.80665f);

    switch (ctrl->phase) {
    case FAILSAFE_PHASE_UNROLL: {
        float roll_err = 0.0f - st->roll_rad;
        out.aileron_cmd = (roll_err * 1.8f - st->gyro_p * 0.25f) * q_scale;
        out.elevator_cmd = (-st->gyro_q * 0.15f) * q_scale;
        out.rudder_cmd = (-st->gyro_r * 0.20f) * q_scale;
        out.throttle_cmd = (st->airspeed_m_s > ctrl->cfg.cruise_airspeed) ? 0.05f : 0.40f;

        if (fabsf(st->roll_rad) < 0.26f && fabsf(st->gyro_p) < 0.35f) {
            ctrl->phase = FAILSAFE_PHASE_PULLOUT;
            ctrl->nz_integral = 0.0f;
        }
        break;
    }

    case FAILSAFE_PHASE_PULLOUT: {
        out.aileron_cmd = (0.0f - st->roll_rad) * 1.5f * q_scale;
        out.rudder_cmd = (-st->gyro_r * 0.20f) * q_scale;

        float target_nz = (ctrl->cfg.max_nz < 2.5f) ? ctrl->cfg.max_nz : 2.5f;
        float nz_err = target_nz - nz_current;
        ctrl->nz_integral += nz_err * dt * 0.5f;
        ctrl->nz_integral = CLAMP(ctrl->nz_integral, -0.2f, 0.4f);

        float elev_demand = nz_err * 0.35f + ctrl->nz_integral - st->gyro_q * 0.15f;
        out.elevator_cmd = elev_demand * q_scale;
        out.throttle_cmd = (st->airspeed_m_s > ctrl->cfg.cruise_airspeed) ? 0.05f : 0.50f;

        if (st->pitch_rad >= -0.05f && st->vz_m_s >= -0.5f) {
            ctrl->phase = FAILSAFE_PHASE_ENERGY_CLIMB;
        }
        break;
    }

    case FAILSAFE_PHASE_ENERGY_CLIMB: {
        out.aileron_cmd = (0.0f - st->roll_rad) * 1.2f * q_scale;
        out.rudder_cmd = (-st->gyro_r * 0.20f) * q_scale;

        float target_pitch = 0.12f;
        if (st->airspeed_m_s < ctrl->cfg.stall_airspeed * 1.3f) {
            target_pitch = 0.02f;
        }

        float pitch_err = target_pitch - st->pitch_rad;
        out.elevator_cmd = (pitch_err * 1.4f - st->gyro_q * 0.20f) * q_scale;
        out.throttle_cmd = 0.85f;

        if (st->altitude_m >= ctrl->cfg.safe_altitude &&
            st->airspeed_m_s >= ctrl->cfg.stall_airspeed * 1.35f) {
            ctrl->phase = FAILSAFE_PHASE_HANDOFF;
        }
        break;
    }

    case FAILSAFE_PHASE_HANDOFF: {
        out.aileron_cmd = (0.0f - st->roll_rad) * 1.0f * q_scale;
        out.elevator_cmd = (0.03f - st->pitch_rad) * 1.0f * q_scale;
        out.rudder_cmd = (-st->gyro_r * 0.20f) * q_scale;
        out.throttle_cmd = 0.60f;
        out.ready_for_rtl = true;
        break;
    }
    }

    out.aileron_cmd = CLAMP(out.aileron_cmd, -1.0f, 1.0f);
    out.elevator_cmd = CLAMP(out.elevator_cmd, -1.0f, 1.0f);
    out.rudder_cmd = CLAMP(out.rudder_cmd, -1.0f, 1.0f);
    out.throttle_cmd = CLAMP(out.throttle_cmd, 0.0f, 1.0f);

    return out;
}

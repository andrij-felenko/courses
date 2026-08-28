#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PREARM_BIT_IMU_OK       (1U << 0)
#define PREARM_BIT_MAG_OK       (1U << 1)
#define PREARM_BIT_BARO_OK      (1U << 2)
#define PREARM_BIT_BATTERY_OK   (1U << 3)
#define PREARM_BIT_RC_SAFE      (1U << 4)
#define PREARM_BIT_EKF_OK       (1U << 5)
#define PREARM_BIT_SAFETY_SW    (1U << 6)

#define PREARM_ALL_REQUIRED     (PREARM_BIT_IMU_OK | \
                                 PREARM_BIT_MAG_OK | \
                                 PREARM_BIT_BARO_OK | \
                                 PREARM_BIT_BATTERY_OK | \
                                 PREARM_BIT_RC_SAFE | \
                                 PREARM_BIT_EKF_OK | \
                                 PREARM_BIT_SAFETY_SW)

typedef enum {
    VEHICLE_DISARMED = 0,
    VEHICLE_ARMED,
    VEHICLE_FAILSAFE
} vehicle_arm_state_t;

typedef struct {
    float cell_voltage;
    float throttle_stick;
    float ekf_pos_variance;
    float gyro_drift_rad_s;
    bool  imu_calibrated;
    bool  mag_calibrated;
    bool  baro_healthy;
    bool  safety_switch_pressed;
} sensor_snapshot_t;

typedef struct {
    vehicle_arm_state_t state;
    uint32_t current_mask;
    uint32_t stable_counter_ms;
    const char *last_failure_reason;
} prearm_evaluator_t;

void prearm_init(prearm_evaluator_t *eval) {
    memset(eval, 0, sizeof(*eval));
    eval->state = VEHICLE_DISARMED;
    eval->last_failure_reason = "System initialized in DISARMED state";
}

void prearm_update(prearm_evaluator_t *eval, const sensor_snapshot_t *s, uint32_t dt_ms) {
    uint32_t mask = 0;

    if (s->imu_calibrated && s->gyro_drift_rad_s < 0.05f) {
        mask |= PREARM_BIT_IMU_OK;
    }
    if (s->mag_calibrated) {
        mask |= PREARM_BIT_MAG_OK;
    }
    if (s->baro_healthy) {
        mask |= PREARM_BIT_BARO_OK;
    }
    if (s->cell_voltage >= 3.70f) {
        mask |= PREARM_BIT_BATTERY_OK;
    }
    if (s->throttle_stick <= 0.05f) {
        mask |= PREARM_BIT_RC_SAFE;
    }
    if (s->ekf_pos_variance < 0.80f) {
        mask |= PREARM_BIT_EKF_OK;
    }
    if (s->safety_switch_pressed) {
        mask |= PREARM_BIT_SAFETY_SW;
    }

    eval->current_mask = mask;

    if ((mask & PREARM_ALL_REQUIRED) == PREARM_ALL_REQUIRED) {
        eval->stable_counter_ms += dt_ms;
    } else {
        eval->stable_counter_ms = 0;
    }
}

bool prearm_request_arm(prearm_evaluator_t *eval) {
    if (eval->state == VEHICLE_ARMED) {
        return true;
    }
    if (eval->state == VEHICLE_FAILSAFE) {
        eval->last_failure_reason = "Cannot arm: Failsafe lockout active";
        return false;
    }

    if ((eval->current_mask & PREARM_ALL_REQUIRED) != PREARM_ALL_REQUIRED) {
        if (!(eval->current_mask & PREARM_BIT_IMU_OK)) {
            eval->last_failure_reason = "IMU uncalibrated or high gyro drift";
        } else if (!(eval->current_mask & PREARM_BIT_MAG_OK)) {
            eval->last_failure_reason = "Compass uncalibrated or inconsistent";
        } else if (!(eval->current_mask & PREARM_BIT_BATTERY_OK)) {
            eval->last_failure_reason = "Battery cell voltage below 3.70V";
        } else if (!(eval->current_mask & PREARM_BIT_RC_SAFE)) {
            eval->last_failure_reason = "Throttle stick not at minimum";
        } else if (!(eval->current_mask & PREARM_BIT_EKF_OK)) {
            eval->last_failure_reason = "EKF position variance too high";
        } else if (!(eval->current_mask & PREARM_BIT_SAFETY_SW)) {
            eval->last_failure_reason = "Hardware safety switch not pressed";
        } else {
            eval->last_failure_reason = "General sensor failure";
        }
        return false;
    }

    if (eval->stable_counter_ms < 1500) {
        eval->last_failure_reason = "Sensors not stable long enough (< 1.5s)";
        return false;
    }

    eval->state = VEHICLE_ARMED;
    eval->last_failure_reason = "Armed successfully";
    return true;
}

void prearm_force_disarm(prearm_evaluator_t *eval, const char *reason) {
    eval->state = VEHICLE_DISARMED;
    eval->last_failure_reason = reason;
}

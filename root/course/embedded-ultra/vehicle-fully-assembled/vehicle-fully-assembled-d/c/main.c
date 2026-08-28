#include <stdint.h>
#include <stdbool.h>

#define PREARM_OK_IMU           (1U << 0)
#define PREARM_OK_MAG           (1U << 1)
#define PREARM_OK_BARO          (1U << 2)
#define PREARM_OK_BATTERY       (1U << 3)
#define PREARM_OK_RC_THROTTLE   (1U << 4)
#define PREARM_OK_EKF           (1U << 5)
#define PREARM_OK_SAFETY_SW     (1U << 6)

#define PREARM_MASK_CRITICAL    (PREARM_OK_IMU | \
                                 PREARM_OK_MAG | \
                                 PREARM_OK_BARO | \
                                 PREARM_OK_BATTERY | \
                                 PREARM_OK_RC_THROTTLE | \
                                 PREARM_OK_EKF | \
                                 PREARM_OK_SAFETY_SW)

typedef enum {
    STATE_DISARMED = 0,
    STATE_ARMED,
    STATE_FAILSAFE_LOCKED
} arm_state_t;

typedef struct {
    float battery_cell_volts;
    float throttle_percent;
    float ekf_variance_pos;
    float gyro_drift_norm;
    bool  accel_calibrated;
    bool  compass_calibrated;
    bool  baro_ready;
    bool  safety_switch_closed;
} vehicle_telemetry_t;

typedef struct {
    arm_state_t state;
    uint32_t    status_mask;
    uint32_t    stable_duration_ms;
    const char *error_msg;
} arm_controller_t;

void arm_controller_init(arm_controller_t *ctrl) {
    ctrl->state = STATE_DISARMED;
    ctrl->status_mask = 0;
    ctrl->stable_duration_ms = 0;
    ctrl->error_msg = "Disarmed on boot";
}

void arm_controller_poll_checks(arm_controller_t *ctrl, const vehicle_telemetry_t *telem, uint32_t dt_ms) {
    uint32_t mask = 0;

    if (telem->accel_calibrated && telem->gyro_drift_norm < 0.05f) {
        mask |= PREARM_OK_IMU;
    }
    if (telem->compass_calibrated) {
        mask |= PREARM_OK_MAG;
    }
    if (telem->baro_ready) {
        mask |= PREARM_OK_BARO;
    }
    if (telem->battery_cell_volts >= 3.70f) {
        mask |= PREARM_OK_BATTERY;
    }
    if (telem->throttle_percent <= 0.05f) {
        mask |= PREARM_OK_RC_THROTTLE;
    }
    if (telem->ekf_variance_pos < 0.80f) {
        mask |= PREARM_OK_EKF;
    }
    if (telem->safety_switch_closed) {
        mask |= PREARM_OK_SAFETY_SW;
    }

    ctrl->status_mask = mask;

    if ((mask & PREARM_MASK_CRITICAL) == PREARM_MASK_CRITICAL) {
        ctrl->stable_duration_ms += dt_ms;
    } else {
        ctrl->stable_duration_ms = 0;
    }
}

bool arm_controller_try_arm(arm_controller_t *ctrl) {
    if (ctrl->state == STATE_ARMED) {
        return true;
    }
    if (ctrl->state == STATE_FAILSAFE_LOCKED) {
        ctrl->error_msg = "Arming rejected: Failsafe lockout";
        return false;
    }

    if ((ctrl->status_mask & PREARM_MASK_CRITICAL) != PREARM_MASK_CRITICAL) {
        if (!(ctrl->status_mask & PREARM_OK_IMU)) {
            ctrl->error_msg = "Pre-arm: Accel not calibrated or gyro moving";
        } else if (!(ctrl->status_mask & PREARM_OK_BATTERY)) {
            ctrl->error_msg = "Pre-arm: Battery low (< 3.70V/cell)";
        } else if (!(ctrl->status_mask & PREARM_OK_RC_THROTTLE)) {
            ctrl->error_msg = "Pre-arm: Throttle stick not at bottom";
        } else if (!(ctrl->status_mask & PREARM_OK_SAFETY_SW)) {
            ctrl->error_msg = "Pre-arm: Safety button not pressed";
        } else {
            ctrl->error_msg = "Pre-arm: Navigation or sensor checks failed";
        }
        return false;
    }

    if (ctrl->stable_duration_ms < 1500) {
        ctrl->error_msg = "Pre-arm: Telemetry not stable for 1.5s";
        return false;
    }

    ctrl->state = STATE_ARMED;
    ctrl->error_msg = "Armed: Motors live";
    return true;
}

void arm_controller_disarm(arm_controller_t *ctrl, const char *reason) {
    ctrl->state = STATE_DISARMED;
    ctrl->error_msg = reason;
}

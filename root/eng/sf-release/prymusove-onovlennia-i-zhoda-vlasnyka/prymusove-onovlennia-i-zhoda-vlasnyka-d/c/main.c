#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>

#define INTERLOCK_SPEED_ZERO     (1U << 0)
#define INTERLOCK_BRAKE_ENGAGED  (1U << 1)
#define INTERLOCK_BATTERY_OK     (1U << 2)
#define INTERLOCK_ACTUATORS_OFF  (1U << 3)
#define INTERLOCK_FS_DRAINED     (1U << 4)

#define INTERLOCKS_REQUIRED_MASK (INTERLOCK_SPEED_ZERO | \
                                  INTERLOCK_BRAKE_ENGAGED | \
                                  INTERLOCK_BATTERY_OK | \
                                  INTERLOCK_ACTUATORS_OFF | \
                                  INTERLOCK_FS_DRAINED)

typedef enum {
    URGENCY_STANDARD_FEATURE = 0,
    URGENCY_IMPORTANT_BUGFIX = 1,
    URGENCY_MANDATORY_REGULATORY = 2,
    URGENCY_CRITICAL_ZERO_DAY = 3,
    URGENCY_SAFETY_EMERGENCY_RECALL = 4
} update_urgency_t;

typedef enum {
    DECISION_NOTIFY_AND_WAIT,
    DECISION_ALLOW_DEFERRAL,
    DECISION_FORCE_IMMEDIATE_SAFE_WINDOW,
    DECISION_SAFETY_HOLD_WAITING_CONDITIONS,
    DECISION_EXECUTE_REBOOT_AND_SWITCH
} policy_decision_t;

typedef struct {
    update_urgency_t urgency;
    time_t issued_at;
    time_t hard_deadline;
    uint32_t max_deferrals;
    uint32_t deferrals_used;
    uint32_t stability_hold_sec;
} update_policy_state_t;

typedef struct {
    double velocity_mps;
    bool parking_brake;
    uint8_t battery_soc_percent;
    bool is_ac_connected;
    double actuator_current_amps;
    bool filesystem_drained;
} vehicle_telemetry_t;

static uint32_t evaluate_interlocks(const vehicle_telemetry_t* telem) {
    uint32_t mask = 0;
    if (telem->velocity_mps >= -0.01 && telem->velocity_mps <= 0.01) {
        mask |= INTERLOCK_SPEED_ZERO;
    }
    if (telem->parking_brake) {
        mask |= INTERLOCK_BRAKE_ENGAGED;
    }
    if (telem->battery_soc_percent >= 50 || telem->is_ac_connected) {
        mask |= INTERLOCK_BATTERY_OK;
    }
    if (telem->actuator_current_amps >= -0.05 && telem->actuator_current_amps <= 0.05) {
        mask |= INTERLOCK_ACTUATORS_OFF;
    }
    if (telem->filesystem_drained) {
        mask |= INTERLOCK_FS_DRAINED;
    }
    return mask;
}

policy_decision_t policy_engine_evaluate(
    const update_policy_state_t* policy,
    const vehicle_telemetry_t* telem,
    time_t current_time,
    time_t safe_conditions_held_since_sec)
{
    bool deadline_expired = (current_time >= policy->hard_deadline);
    bool deferrals_exhausted = (policy->deferrals_used >= policy->max_deferrals);
    bool must_force = deadline_expired || deferrals_exhausted || 
                       (policy->urgency == URGENCY_SAFETY_EMERGENCY_RECALL);

    if (!must_force) {
        return DECISION_ALLOW_DEFERRAL;
    }

    uint32_t current_mask = evaluate_interlocks(telem);
    if ((current_mask & INTERLOCKS_REQUIRED_MASK) != INTERLOCKS_REQUIRED_MASK) {
        return DECISION_SAFETY_HOLD_WAITING_CONDITIONS;
    }

    if (safe_conditions_held_since_sec > 0 && 
        (current_time - safe_conditions_held_since_sec) >= (time_t)policy->stability_hold_sec) {
        return DECISION_EXECUTE_REBOOT_AND_SWITCH;
    }

    return DECISION_FORCE_IMMEDIATE_SAFE_WINDOW;
}

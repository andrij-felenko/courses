#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HW_FAMILY_MAX_LEN 32
#define MAX_ALLOWED_POSTPONES 5

typedef enum {
    SEVERITY_FEATURE = 1,
    SEVERITY_MAINTENANCE = 2,
    SEVERITY_SECURITY_STANDARD = 3,
    SEVERITY_CRITICAL_SECURITY = 4
} UpdateSeverity;

typedef enum {
    OP_STATE_SHUTDOWN = 0,
    OP_STATE_IDLE = 1,
    OP_STATE_STANDBY = 2,
    OP_STATE_ACTIVE_MISSION = 3,
    OP_STATE_EMERGENCY = 4
} DeviceOperatingState;

typedef enum {
    BEARER_ETHERNET = (1 << 0),
    BEARER_WIFI = (1 << 1),
    BEARER_CELLULAR_UNMETERED = (1 << 2),
    BEARER_CELLULAR_METERED = (1 << 3)
} NetworkBearerMask;

typedef struct {
    char hardware_family[HW_FAMILY_MAX_LEN];
    uint32_t hardware_revision_mask;
    uint32_t security_version;
    UpdateSeverity severity;
    uint8_t min_battery_soc_pct;
    uint16_t min_battery_voltage_mv;
    int8_t temp_min_c;
    int8_t temp_max_c;
    uint32_t allowed_bearers_mask;
    uint8_t max_postpones;
} PolicyManifest;

typedef struct {
    char hardware_family[HW_FAMILY_MAX_LEN];
    uint32_t hardware_revision_bit;
    uint32_t current_security_version;
    DeviceOperatingState operating_state;
    uint8_t battery_soc_pct;
    uint16_t battery_voltage_mv;
    int8_t board_temperature_c;
    NetworkBearerMask current_bearer;
    bool is_in_maintenance_window;
    uint8_t current_postpone_count;
} DeviceTelemetry;

typedef enum {
    POLICY_DECISION_ACCEPT_NOW = 0,
    POLICY_DECISION_POSTPONE_BUSY = 1,
    POLICY_DECISION_POSTPONE_OUTSIDE_WINDOW = 2,
    POLICY_REJECT_HW_FAMILY_MISMATCH = 10,
    POLICY_REJECT_HW_REV_UNSUPPORTED = 11,
    POLICY_REJECT_ANTI_ROLLBACK = 12,
    POLICY_REJECT_BATTERY_LOW = 13,
    POLICY_REJECT_TEMPERATURE_LIMIT = 14,
    POLICY_REJECT_BEARER_DISALLOWED = 15
} PolicyDecisionCode;

PolicyDecisionCode evaluate_update_policy(const PolicyManifest *manifest,
                                         const DeviceTelemetry *telemetry) {
    if (!manifest || !telemetry) {
        return POLICY_REJECT_HW_FAMILY_MISMATCH;
    }

    /* 1. Апаратна ідентифікація */
    if (strncmp(manifest->hardware_family, telemetry->hardware_family, HW_FAMILY_MAX_LEN) != 0) {
        return POLICY_REJECT_HW_FAMILY_MISMATCH;
    }

    if ((manifest->hardware_revision_mask & telemetry->hardware_revision_bit) == 0) {
        return POLICY_REJECT_HW_REV_UNSUPPORTED;
    }

    /* 2. Захист від відкату на вразливу версію */
    if (manifest->security_version < telemetry->current_security_version) {
        return POLICY_REJECT_ANTI_ROLLBACK;
    }

    /* 3. Перевірка мережевого носія */
    if ((manifest->allowed_bearers_mask & telemetry->current_bearer) == 0) {
        return POLICY_REJECT_BEARER_DISALLOWED;
    }

    /* 4. Енергетичні та температурні обмеження */
    uint8_t effective_soc_limit = manifest->min_battery_soc_pct;
    uint16_t effective_volt_limit = manifest->min_battery_voltage_mv;

    /* Для критичного Zero-Day знижуємо бар'єр заряду для якнайшвидшого латання */
    if (manifest->severity == SEVERITY_CRITICAL_SECURITY) {
        if (effective_soc_limit > 30) {
            effective_soc_limit = 30;
        }
        if (effective_volt_limit > 3500) {
            effective_volt_limit = 3500;
        }
    }

    if (telemetry->battery_soc_pct < effective_soc_limit ||
        telemetry->battery_voltage_mv < effective_volt_limit) {
        return POLICY_REJECT_BATTERY_LOW;
    }

    if (telemetry->board_temperature_c < manifest->temp_min_c ||
        telemetry->board_temperature_c > manifest->temp_max_c) {
        return POLICY_REJECT_TEMPERATURE_LIMIT;
    }

    /* 5. Операційний стан і вікно оновлення */
    bool is_emergency = (manifest->severity == SEVERITY_CRITICAL_SECURITY);

    if (telemetry->operating_state == OP_STATE_ACTIVE_MISSION ||
        telemetry->operating_state == OP_STATE_EMERGENCY) {
        /* Пристрій виконує критичну роботу: навіть Zero-Day не повинен ламати керованість */
        return POLICY_DECISION_POSTPONE_BUSY;
    }

    if (!is_emergency) {
        bool postpone_limit_reached = (telemetry->current_postpone_count >= manifest->max_postpones);

        if (!telemetry->is_in_maintenance_window && !postpone_limit_reached) {
            return POLICY_DECISION_POSTPONE_OUTSIDE_WINDOW;
        }
    }

    return POLICY_DECISION_ACCEPT_NOW;
}

/* contact_diagnostics.h / contact_diagnostics.c */
#include <stdint.h>
#include <stdbool.h>

#define MAX_ALLOWED_CONTACT_RESISTANCE_MOHM  40.0f
#define MIN_BATTERY_VOLTAGE_MV               18000
#define MAX_BATTERY_VOLTAGE_MV               25500
#define MAX_CELL_TEMPERATURE_C               45.0f

typedef enum {
    DOCK_CONTACT_OPEN = 0,
    DOCK_CONTACT_PROBING,
    DOCK_CONTACT_POLARITY_FAULT,
    DOCK_CONTACT_HIGH_RESISTANCE,
    DOCK_CONTACT_COMM_TIMEOUT,
    DOCK_CONTACT_READY_TO_CHARGE,
    DOCK_CONTACT_CHARGING_ACTIVE,
    DOCK_CONTACT_THERMAL_FAULT
} dock_contact_state_t;

typedef struct {
    float sense_voltage_drop_mv;
    float probe_current_ma;
    float calculated_resistance_mohm;
    uint32_t battery_voltage_mv;
    float max_cell_temp_c;
    bool reverse_polarity_detected;
    bool bms_heartbeat_alive;
} dock_telemetry_t;

typedef struct {
    dock_contact_state_t state;
    uint32_t state_entry_time_ms;
    uint8_t retry_count;
} dock_charge_controller_t;

void dock_charge_controller_init(dock_charge_controller_t *ctrl) {
    if (!ctrl) return;
    ctrl->state = DOCK_CONTACT_OPEN;
    ctrl->state_entry_time_ms = 0;
    ctrl->retry_count = 0;
}

dock_contact_state_t dock_evaluate_contact_health(
    dock_charge_controller_t *ctrl,
    const dock_telemetry_t *telem,
    uint32_t current_time_ms)
{
    if (!ctrl || !telem) return DOCK_CONTACT_OPEN;

    switch (ctrl->state) {
    case DOCK_CONTACT_OPEN:
        if (telem->probe_current_ma > 50.0f) {
            ctrl->state = DOCK_CONTACT_PROBING;
            ctrl->state_entry_time_ms = current_time_ms;
        }
        break;

    case DOCK_CONTACT_PROBING:
        if (telem->reverse_polarity_detected) {
            ctrl->state = DOCK_CONTACT_POLARITY_FAULT;
            break;
        }

        if (telem->probe_current_ma > 10.0f) {
            float r_mohm = (telem->sense_voltage_drop_mv / telem->probe_current_ma) * 1000.0f;
            if (r_mohm > MAX_ALLOWED_CONTACT_RESISTANCE_MOHM) {
                ctrl->state = DOCK_CONTACT_HIGH_RESISTANCE;
                break;
            }
        }

        if (!telem->bms_heartbeat_alive) {
            if (current_time_ms - ctrl->state_entry_time_ms > 1000) {
                ctrl->state = DOCK_CONTACT_COMM_TIMEOUT;
            }
            break;
        }

        if (telem->battery_voltage_mv < MIN_BATTERY_VOLTAGE_MV ||
            telem->battery_voltage_mv > MAX_BATTERY_VOLTAGE_MV) {
            ctrl->state = DOCK_CONTACT_POLARITY_FAULT;
            break;
        }

        if (telem->max_cell_temp_c > MAX_CELL_TEMPERATURE_C) {
            ctrl->state = DOCK_CONTACT_THERMAL_FAULT;
            break;
        }

        ctrl->state = DOCK_CONTACT_READY_TO_CHARGE;
        break;

    case DOCK_CONTACT_READY_TO_CHARGE:
        /* Готовий до комутації реле через soft-start */
        break;

    case DOCK_CONTACT_CHARGING_ACTIVE:
        if (telem->max_cell_temp_c > MAX_CELL_TEMPERATURE_C ||
            !telem->bms_heartbeat_alive) {
            ctrl->state = DOCK_CONTACT_THERMAL_FAULT;
        }
        break;

    default:
        break;
    }

    return ctrl->state;
}

// ============================================================================
// limp_controller.h - C99 API Контролера кульгавого режиму
// ============================================================================
#ifndef LIMP_CONTROLLER_H
#define LIMP_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define LIMP_DTC_RING_SIZE 16

typedef enum {
    LIMP_STATE_NORMAL       = 0,
    LIMP_STATE_THROTTLED    = 1,
    LIMP_STATE_L1           = 2,
    LIMP_STATE_L2           = 3,
    LIMP_STATE_CRITICAL_LAND= 4,
    LIMP_STATE_LATCHED      = 5,
    LIMP_STATE_COUNT
} limp_state_t;

typedef enum {
    LIMP_EVENT_NONE         = 0,
    LIMP_EVENT_WARN         = 1,
    LIMP_EVENT_CRIT_1       = 2,
    LIMP_EVENT_CRIT_2       = 3,
    LIMP_EVENT_FATAL        = 4,
    LIMP_EVENT_COUNT
} limp_event_severity_t;

typedef enum {
    DTC_CODE_OK                 = 0x0000,
    DTC_CODE_MOSFET_OVERTEMP    = 0x1001,
    DTC_CODE_MOTOR_OVERTEMP     = 0x1002,
    DTC_CODE_BATTERY_SAG        = 0x2001,
    DTC_CODE_CELL_UNBALANCE     = 0x2002,
    DTC_CODE_CURRENT_SENSE_FAIL = 0x3001,
    DTC_CODE_COMM_LINK_TIMEOUT  = 0x4001,
    DTC_CODE_DESCENT_STALL      = 0x5001
} dtc_code_t;

typedef struct {
    float mosfet_temp_c;
    float motor_temp_c;
    float bus_voltage_v;
    float min_cell_voltage_v;
    float total_current_a;
    bool  current_sensors_healthy;
    bool  telemetry_link_healthy;
    uint32_t timestamp_ms;
} limp_sensor_telemetry_t;

typedef struct {
    float max_allowed_current_a;
    uint32_t target_pwm_freq_hz;
    bool  enable_tier1_nav;
    bool  enable_tier2_sbc;
    bool  enable_tier3_payload;
    limp_state_t current_state;
    dtc_code_t   active_primary_dtc;
    uint32_t     total_dtc_count;
} limp_control_outputs_t;

typedef struct {
    float temp_warn_c;
    float temp_crit_c;
    float temp_fatal_c;
    float temp_hysteresis_c;
    float cell_volt_warn_v;
    float cell_volt_crit_v;
    float nominal_current_max_a;
    float limp_l1_current_max_a;
    float limp_l2_current_max_a;
    uint32_t min_dwell_time_ms;
} limp_config_t;

typedef struct {
    dtc_code_t code;
    uint8_t    subsystem_id;
    uint32_t   timestamp_ms;
    float      mosfet_temp_c;
    float      bus_voltage_v;
    float      min_cell_voltage_v;
    float      total_current_a;
    uint16_t   crc16;
} limp_freeze_frame_t;

typedef struct {
    limp_freeze_frame_t records[LIMP_DTC_RING_SIZE];
    uint32_t head;
    uint32_t count;
    uint32_t total_recorded;
} limp_dtc_ring_buffer_t;

typedef struct {
    limp_config_t          config;
    limp_state_t           current_state;
    uint32_t               state_entry_time_ms;
    dtc_code_t             primary_active_dtc;
    limp_dtc_ring_buffer_t dtc_buffer;
    bool                   initialized;
} limp_controller_t;

void limp_controller_init(limp_controller_t *ctrl, const limp_config_t *cfg);
void limp_controller_step(limp_controller_t *ctrl,
                          const limp_sensor_telemetry_t *telem,
                          limp_control_outputs_t *outputs);
bool limp_controller_get_dtc_record(const limp_controller_t *ctrl,
                                    uint32_t index,
                                    limp_freeze_frame_t *out_record);

#ifdef __cplusplus
}
#endif

#endif // LIMP_CONTROLLER_H

// ============================================================================
// limp_controller.c - C99 Реалізація
// ============================================================================
#include <string.h>

// Розрахунок CRC16-CCITT для захисту Freeze Frame
static uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

// Статична таблиця базових переходів автомата станів
static const limp_state_t s_transition_matrix[LIMP_STATE_COUNT][LIMP_EVENT_COUNT] = {
    // STATE_NORMAL
    { LIMP_STATE_NORMAL, LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_THROTTLED
    { LIMP_STATE_NORMAL, LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_LIMP_L1
    { LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_LIMP_L2 (з L2 повернення вгору заборонено)
    { LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_CRITICAL_LAND
    { LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_LATCHED },
    // STATE_LATCHED
    { LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED }
};

static void push_dtc(limp_controller_t *ctrl, dtc_code_t code, uint8_t sub_id, const limp_sensor_telemetry_t *t) {
    limp_dtc_ring_buffer_t *buf = &ctrl->dtc_buffer;
    limp_freeze_frame_t *slot = &buf->records[buf->head];

    slot->code = code;
    slot->subsystem_id = sub_id;
    slot->timestamp_ms = t->timestamp_ms;
    slot->mosfet_temp_c = t->mosfet_temp_c;
    slot->bus_voltage_v = t->bus_voltage_v;
    slot->min_cell_voltage_v = t->min_cell_voltage_v;
    slot->total_current_a = t->total_current_a;
    slot->crc16 = calculate_crc16((const uint8_t*)slot, offsetof(limp_freeze_frame_t, crc16));

    buf->head = (buf->head + 1) % LIMP_DTC_RING_SIZE;
    if (buf->count < LIMP_DTC_RING_SIZE) {
        buf->count++;
    }
    buf->total_recorded++;

    if (ctrl->primary_active_dtc == DTC_CODE_OK) {
        ctrl->primary_active_dtc = code;
    }
}

void limp_controller_init(limp_controller_t *ctrl, const limp_config_t *cfg) {
    if (!ctrl || !cfg) return;
    memset(ctrl, 0, sizeof(limp_controller_t));
    ctrl->config = *cfg;
    ctrl->current_state = LIMP_STATE_NORMAL;
    ctrl->state_entry_time_ms = 0;
    ctrl->primary_active_dtc = DTC_CODE_OK;
    ctrl->initialized = true;
}

static limp_event_severity_t classify_telemetry(const limp_controller_t *ctrl,
                                                const limp_sensor_telemetry_t *t,
                                                dtc_code_t *detected_dtc) {
    *detected_dtc = DTC_CODE_OK;

    if (!t->current_sensors_healthy) {
        *detected_dtc = DTC_CODE_CURRENT_SENSE_FAIL;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_fatal_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->min_cell_voltage_v <= ctrl->config.cell_volt_crit_v) {
        *detected_dtc = DTC_CODE_BATTERY_SAG;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_crit_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_CRIT_1;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_warn_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_WARN;
    }
    if (t->min_cell_voltage_v <= ctrl->config.cell_volt_warn_v) {
        *detected_dtc = DTC_CODE_BATTERY_SAG;
        return LIMP_EVENT_WARN;
    }

    return LIMP_EVENT_NONE;
}

void limp_controller_step(limp_controller_t *ctrl,
                          const limp_sensor_telemetry_t *telem,
                          limp_control_outputs_t *outputs) {
    if (!ctrl || !telem || !outputs || !ctrl->initialized) return;

    dtc_code_t active_event_dtc = DTC_CODE_OK;
    limp_event_severity_t severity = classify_telemetry(ctrl, telem, &active_event_dtc);

    if (active_event_dtc != DTC_CODE_OK) {
        if (ctrl->primary_active_dtc != active_event_dtc) {
            push_dtc(ctrl, active_event_dtc, 0x01, telem);
        }
    }

    limp_state_t target_state = s_transition_matrix[ctrl->current_state][severity];
    uint32_t time_in_state = telem->timestamp_ms - ctrl->state_entry_time_ms;

    if (target_state < ctrl->current_state) {
        bool allow_recovery = false;
        if (time_in_state >= ctrl->config.min_dwell_time_ms) {
            if (ctrl->current_state == LIMP_STATE_THROTTLED && severity == LIMP_EVENT_NONE) {
                if (telem->mosfet_temp_c <= (ctrl->config.temp_warn_c - ctrl->config.temp_hysteresis_c) &&
                    telem->min_cell_voltage_v >= (ctrl->config.cell_volt_warn_v + 0.15f)) {
                    allow_recovery = true;
                }
            } else if (ctrl->current_state == LIMP_STATE_L1 && severity <= LIMP_EVENT_WARN) {
                if (telem->mosfet_temp_c <= (ctrl->config.temp_crit_c - ctrl->config.temp_hysteresis_c)) {
                    allow_recovery = true;
                }
            }
        }
        if (!allow_recovery) {
            target_state = ctrl->current_state;
        }
    }

    if (target_state != ctrl->current_state) {
        ctrl->current_state = target_state;
        ctrl->state_entry_time_ms = telem->timestamp_ms;
    }

    outputs->current_state = ctrl->current_state;
    outputs->active_primary_dtc = ctrl->primary_active_dtc;
    outputs->total_dtc_count = ctrl->dtc_buffer.total_recorded;

    switch (ctrl->current_state) {
        case LIMP_STATE_NORMAL:
            outputs->max_allowed_current_a = ctrl->config.nominal_current_max_a;
            outputs->target_pwm_freq_hz = 25000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = true;
            break;

        case LIMP_STATE_THROTTLED: {
            float t_ratio = (ctrl->config.temp_crit_c - telem->mosfet_temp_c) /
                            (ctrl->config.temp_crit_c - ctrl->config.temp_warn_c);
            if (t_ratio < 0.0f) t_ratio = 0.0f;
            if (t_ratio > 1.0f) t_ratio = 1.0f;

            outputs->max_allowed_current_a = ctrl->config.limp_l1_current_max_a +
                t_ratio * (ctrl->config.nominal_current_max_a - ctrl->config.limp_l1_current_max_a);
            outputs->target_pwm_freq_hz = 16000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = true;
            break;
        }

        case LIMP_STATE_L1:
            outputs->max_allowed_current_a = ctrl->config.limp_l1_current_max_a;
            outputs->target_pwm_freq_hz = 10000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = false;
            break;

        case LIMP_STATE_L2:
        case LIMP_STATE_CRITICAL_LAND:
        case LIMP_STATE_LATCHED:
        default:
            outputs->max_allowed_current_a = ctrl->config.limp_l2_current_max_a;
            outputs->target_pwm_freq_hz = 8000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = false;
            outputs->enable_tier3_payload = false;
            break;
    }
}

bool limp_controller_get_dtc_record(const limp_controller_t *ctrl,
                                    uint32_t index,
                                    limp_freeze_frame_t *out_record) {
    if (!ctrl || !out_record || index >= ctrl->dtc_buffer.count) return false;
    uint32_t actual_idx = (ctrl->dtc_buffer.head + LIMP_DTC_RING_SIZE - ctrl->dtc_buffer.count + index) % LIMP_DTC_RING_SIZE;
    *out_record = ctrl->dtc_buffer.records[actual_idx];
    return true;
}

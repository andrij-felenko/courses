#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define TELEMETRY_RING_SIZE 256
#define MAX_SCENARIO_STEPS  16
#define MAX_CHANNELS        4

typedef enum {
    STRESS_TEMPERATURE_COLD,
    STRESS_TEMPERATURE_HOT,
    STRESS_VIBRATION_RANDOM,
    STRESS_COMBINED
} StressType;

typedef enum {
    STATE_IDLE,
    STATE_RAMP,
    STATE_DWELL,
    STATE_RECOVERY_CHECK,
    STATE_EMERGENCY_ABORT,
    STATE_COMPLETE
} HaltState;

typedef enum {
    FAULT_NONE = 0,
    FAULT_VOLTAGE_SAG        = (1 << 0),
    FAULT_OVERCURRENT        = (1 << 1),
    FAULT_THERMAL_RUNAWAY    = (1 << 2),
    FAULT_COMM_TIMEOUT       = (1 << 3),
    FAULT_CRC_ERROR_BURST    = (1 << 4),
    FAULT_VIBRATION_OVERLOAD = (1 << 5)
} FaultFlags;

typedef struct {
    uint32_t timestamp_ms;
    float chamber_temp_c;
    float dut_hotspot_temp_c;
    float supply_voltage_v[MAX_CHANNELS];
    float supply_current_ma[MAX_CHANNELS];
    float vibration_g_rms;
    uint16_t comm_crc_errors;
    bool comm_alive;
    uint32_t fault_mask;
} TelemetrySnapshot;

typedef struct {
    StressType type;
    float target_value;       /* °C або g_rms */
    float ramp_rate_per_min;  /* °C/хв або g_rms/хв */
    uint32_t dwell_time_sec;  /* час витримки */
    float voltage_margin_pct; /* відхилення напруги ±% */
} StepConfig;

typedef struct {
    float max_allowed_current_ma[MAX_CHANNELS];
    float min_allowed_voltage_v[MAX_CHANNELS];
    float max_allowed_voltage_v[MAX_CHANNELS];
    float max_dut_temp_c;
    float max_temp_slew_c_per_sec;
    float max_vibration_g_rms;
    uint32_t max_consecutive_comm_failures;
} SafetyThresholds;

typedef struct {
    TelemetrySnapshot buffer[TELEMETRY_RING_SIZE];
    size_t head;
    size_t count;
    bool frozen;
} TelemetryRingBuffer;

typedef struct {
    HaltState state;
    StepConfig scenario[MAX_SCENARIO_STEPS];
    size_t total_steps;
    size_t current_step_idx;
    
    SafetyThresholds safety;
    TelemetryRingBuffer ring;
    
    float current_stress_level;
    uint32_t state_timer_ms;
    uint32_t consecutive_comm_failures;
    
    float lol_recorded;
    float uol_recorded;
    float ldl_recorded;
    float udl_recorded;
    bool is_destructive_fault;
} HaltController;

/* Ініціалізація кільцевого буфера */
void ring_init(TelemetryRingBuffer *rb) {
    memset(rb, 0, sizeof(TelemetryRingBuffer));
    rb->head = 0;
    rb->count = 0;
    rb->frozen = false;
}

/* Додавання знімка телеметрії */
void ring_push(TelemetryRingBuffer *rb, const TelemetrySnapshot *snap) {
    if (rb->frozen) return;
    rb->buffer[rb->head] = *snap;
    rb->head = (rb->head + 1) % TELEMETRY_RING_SIZE;
    if (rb->count < TELEMETRY_RING_SIZE) {
        rb->count++;
    }
}

/* Ініціалізація контролера HALT */
void halt_controller_init(HaltController *ctrl, const SafetyThresholds *safety) {
    memset(ctrl, 0, sizeof(HaltController));
    ctrl->state = STATE_IDLE;
    ctrl->safety = *safety;
    ring_init(&ctrl->ring);
    ctrl->lol_recorded = 0.0f;
    ctrl->uol_recorded = 0.0f;
    ctrl->ldl_recorded = 0.0f;
    ctrl->udl_recorded = 0.0f;
}

/* Додавання кроку в сценарій */
bool halt_add_step(HaltController *ctrl, StressType type, float target, float ramp_rate, uint32_t dwell_sec, float volt_margin) {
    if (ctrl->total_steps >= MAX_SCENARIO_STEPS) return false;
    StepConfig *step = &ctrl->scenario[ctrl->total_steps++];
    step->type = type;
    step->target_value = target;
    step->ramp_rate_per_min = ramp_rate;
    step->dwell_time_sec = dwell_sec;
    step->voltage_margin_pct = volt_margin;
    return true;
}

/* Перевірка безпеки та виявлення відмов */
uint32_t evaluate_safety_and_faults(HaltController *ctrl, const TelemetrySnapshot *snap, const TelemetrySnapshot *prev_snap) {
    uint32_t faults = FAULT_NONE;

    /* 1. Контроль напруги та струму рейок */
    for (size_t ch = 0; ch < MAX_CHANNELS; ++ch) {
        if (snap->supply_current_ma[ch] > ctrl->safety.max_allowed_current_ma[ch]) {
            faults |= FAULT_OVERCURRENT;
        }
        if (snap->supply_voltage_v[ch] < ctrl->safety.min_allowed_voltage_v[ch] ||
            snap->supply_voltage_v[ch] > ctrl->safety.max_allowed_voltage_v[ch]) {
            faults |= FAULT_VOLTAGE_SAG;
        }
    }

    /* 2. Контроль перегріву та теплового розгону (dT/dt) */
    if (snap->dut_hotspot_temp_c > ctrl->safety.max_dut_temp_c) {
        faults |= FAULT_THERMAL_RUNAWAY;
    }
    if (prev_snap != NULL && snap->timestamp_ms > prev_snap->timestamp_ms) {
        float dt_sec = (float)(snap->timestamp_ms - prev_snap->timestamp_ms) / 1000.0f;
        float dt_temp = fabsf(snap->dut_hotspot_temp_c - prev_snap->dut_hotspot_temp_c);
        if ((dt_temp / dt_sec) > ctrl->safety.max_temp_slew_c_per_sec) {
            faults |= FAULT_THERMAL_RUNAWAY;
        }
    }

    /* 3. Контроль вібраційного перевантаження */
    if (snap->vibration_g_rms > ctrl->safety.max_vibration_g_rms) {
        faults |= FAULT_VIBRATION_OVERLOAD;
    }

    /* 4. Контроль інтерфейсу зв'язку */
    if (!snap->comm_alive) {
        ctrl->consecutive_comm_failures++;
        if (ctrl->consecutive_comm_failures >= ctrl->safety.max_consecutive_comm_failures) {
            faults |= FAULT_COMM_TIMEOUT;
        }
    } else {
        ctrl->consecutive_comm_failures = 0;
    }

    if (snap->comm_crc_errors > 50) {
        faults |= FAULT_CRC_ERROR_BURST;
    }

    return faults;
}

/* Головна функція ітерації FSM (викликається щосекунди або по таймеру) */
void halt_controller_tick(HaltController *ctrl, TelemetrySnapshot *snap, uint32_t dt_ms) {
    static TelemetrySnapshot last_snapshot;
    static bool has_last_snapshot = false;

    snap->fault_mask = evaluate_safety_and_faults(
        ctrl, snap, has_last_snapshot ? &last_snapshot : NULL
    );
    last_snapshot = *snap;
    has_last_snapshot = true;

    ring_push(&ctrl->ring, snap);

    /* Аварійні зупинки при фатальних факторах */
    if (snap->fault_mask & (FAULT_OVERCURRENT | FAULT_THERMAL_RUNAWAY | FAULT_VIBRATION_OVERLOAD)) {
        ctrl->state = STATE_EMERGENCY_ABORT;
        ctrl->ring.frozen = true;
        ctrl->is_destructive_fault = true;
        ctrl->udl_recorded = ctrl->current_stress_level;
        return;
    }

    if (ctrl->current_step_idx >= ctrl->total_steps) {
        ctrl->state = STATE_COMPLETE;
        return;
    }

    StepConfig *curr = &ctrl->scenario[ctrl->current_step_idx];

    switch (ctrl->state) {
    case STATE_IDLE:
        ctrl->current_step_idx = 0;
        ctrl->state_timer_ms = 0;
        ctrl->state = STATE_RAMP;
        break;

    case STATE_RAMP: {
        float ramp_per_ms = curr->ramp_rate_per_min / 60000.0f;
        float delta = ramp_per_ms * (float)dt_ms;

        if (ctrl->current_stress_level < curr->target_value) {
            ctrl->current_stress_level += delta;
            if (ctrl->current_stress_level >= curr->target_value) {
                ctrl->current_stress_level = curr->target_value;
                ctrl->state = STATE_DWELL;
                ctrl->state_timer_ms = 0;
            }
        } else if (ctrl->current_stress_level > curr->target_value) {
            ctrl->current_stress_level -= delta;
            if (ctrl->current_stress_level <= curr->target_value) {
                ctrl->current_stress_level = curr->target_value;
                ctrl->state = STATE_DWELL;
                ctrl->state_timer_ms = 0;
            }
        } else {
            ctrl->state = STATE_DWELL;
            ctrl->state_timer_ms = 0;
        }
        break;
    }

    case STATE_DWELL:
        ctrl->state_timer_ms += dt_ms;

        /* Виявлення функціонального збою в зоні витримки */
        if (snap->fault_mask & (FAULT_COMM_TIMEOUT | FAULT_CRC_ERROR_BURST | FAULT_VOLTAGE_SAG)) {
            ctrl->state = STATE_RECOVERY_CHECK;
            ctrl->state_timer_ms = 0;
            if (curr->type == STRESS_TEMPERATURE_HOT || curr->type == STRESS_VIBRATION_RANDOM) {
                ctrl->uol_recorded = ctrl->current_stress_level;
            } else {
                ctrl->lol_recorded = ctrl->current_stress_level;
            }
        } else if (ctrl->state_timer_ms >= (curr->dwell_time_sec * 1000)) {
            /* Крок пройдено успішно -> наступний ступінь */
            ctrl->current_step_idx++;
            ctrl->state = STATE_RAMP;
            ctrl->state_timer_ms = 0;
        }
        break;

    case STATE_RECOVERY_CHECK:
        ctrl->state_timer_ms += dt_ms;
        /* Даємо 5 секунд на відновлення працездатності */
        if (snap->comm_alive && !(snap->fault_mask & FAULT_VOLTAGE_SAG)) {
            /* Оборотна відмова (UOL/LOL підтверджено) -> продовжуємо тест */
            ctrl->current_step_idx++;
            ctrl->state = STATE_RAMP;
            ctrl->state_timer_ms = 0;
        } else if (ctrl->state_timer_ms >= 5000) {
            /* Зразок не відновився -> необоротна відмова (UDL/LDL) */
            ctrl->is_destructive_fault = true;
            if (curr->type == STRESS_TEMPERATURE_HOT || curr->type == STRESS_VIBRATION_RANDOM) {
                ctrl->udl_recorded = ctrl->current_stress_level;
            } else {
                ctrl->ldl_recorded = ctrl->current_stress_level;
            }
            ctrl->state = STATE_EMERGENCY_ABORT;
            ctrl->ring.frozen = true;
        }
        break;

    case STATE_EMERGENCY_ABORT:
    case STATE_COMPLETE:
        break;
    }
}

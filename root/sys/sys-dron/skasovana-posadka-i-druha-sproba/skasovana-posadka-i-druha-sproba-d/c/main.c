#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_ABORT_ATTEMPTS 2
#define LIDAR_OBSTACLE_THRESHOLD_M 1.5f
#define ATTITUDE_MAX_TILT_RAD 0.436f /* 25 градусів */
#define MISSED_APPROACH_ALT_M 25.0f
#define CLIMB_VELOCITY_SETPOINT_MS 3.0f

typedef enum {
    STATE_APPROACH_DESCENT = 0,
    STATE_ABORT_BRAKE_CLIMB,
    STATE_ENERGY_AUDIT,
    STATE_CIRCUIT_LOITER,
    STATE_EMERGENCY_FAILSAFE
} go_around_state_t;

typedef struct {
    float current_alt_m;
    float vertical_speed_ms;
    float lidar_distance_m;
    float roll_rad;
    float pitch_rad;
    float battery_soc_norm;       /* 0.0 .. 1.0 */
    float battery_voltage_v;
    bool operator_abort_command;
    bool lidar_valid;
} flight_telemetry_t;

typedef struct {
    go_around_state_t state;
    uint8_t abort_counter;
    float target_alt_m;
    float target_vz_ms;
    float target_roll_rad;
    float target_pitch_rad;
    bool climb_priority_active;
    uint32_t state_entry_time_ms;
} go_around_fsm_t;

void go_around_init(go_around_fsm_t *fsm) {
    fsm->state = STATE_APPROACH_DESCENT;
    fsm->abort_counter = 0;
    fsm->target_alt_m = 0.0f;
    fsm->target_vz_ms = -1.0f;
    fsm->target_roll_rad = 0.0f;
    fsm->target_pitch_rad = 0.0f;
    fsm->climb_priority_active = false;
    fsm->state_entry_time_ms = 0;
}

static bool check_abort_triggers(const flight_telemetry_t *telem) {
    if (telem->operator_abort_command) {
        return true;
    }
    if (telem->lidar_valid && (telem->lidar_distance_m < LIDAR_OBSTACLE_THRESHOLD_M)) {
        return true;
    }
    if ((fabsf(telem->roll_rad) > ATTITUDE_MAX_TILT_RAD) || 
        (fabsf(telem->pitch_rad) > ATTITUDE_MAX_TILT_RAD)) {
        return true;
    }
    return false;
}

void go_around_update(go_around_fsm_t *fsm, const flight_telemetry_t *telem, uint32_t now_ms) {
    switch (fsm->state) {
    case STATE_APPROACH_DESCENT:
        fsm->target_vz_ms = -1.0f;
        fsm->climb_priority_active = false;

        if (check_abort_triggers(telem)) {
            fsm->abort_counter++;
            fsm->state = STATE_ABORT_BRAKE_CLIMB;
            fsm->state_entry_time_ms = now_ms;
            fsm->target_alt_m = telem->current_alt_m + MISSED_APPROACH_ALT_M;
        }
        break;

    case STATE_ABORT_BRAKE_CLIMB:
        /* Екстрений вертикальний набір: крен і тангаж затиснуті в 0 */
        fsm->target_vz_ms = CLIMB_VELOCITY_SETPOINT_MS;
        fsm->target_roll_rad = 0.0f;
        fsm->target_pitch_rad = 0.0f;
        fsm->climb_priority_active = true;

        if (telem->current_alt_m >= fsm->target_alt_m) {
            fsm->state = STATE_ENERGY_AUDIT;
            fsm->state_entry_time_ms = now_ms;
        }
        break;

    case STATE_ENERGY_AUDIT:
        fsm->climb_priority_active = false;
        fsm->target_vz_ms = 0.0f; /* Зависання на безпечному ешелоні */

        /* Перевірка ліміту спроб і залишку заряду (мінімум 20% і напруга > 3.5V на банку) */
        if ((fsm->abort_counter >= MAX_ABORT_ATTEMPTS) || 
            (telem->battery_soc_norm < 0.20f) || 
            (telem->battery_voltage_v < 21.0f)) {
            fsm->state = STATE_EMERGENCY_FAILSAFE;
        } else {
            fsm->state = STATE_CIRCUIT_LOITER;
        }
        fsm->state_entry_time_ms = now_ms;
        break;

    case STATE_CIRCUIT_LOITER:
        /* Очікування 10 секунд на колі перед повторним заходом */
        fsm->target_vz_ms = 0.0f;
        if ((now_ms - fsm->state_entry_time_ms) > 10000U) {
            fsm->state = STATE_APPROACH_DESCENT;
            fsm->state_entry_time_ms = now_ms;
        }
        break;

    case STATE_EMERGENCY_FAILSAFE:
        /* Аварійний спуск на поточному місці або відхід */
        fsm->target_vz_ms = -0.6f;
        fsm->climb_priority_active = false;
        break;
    }
}

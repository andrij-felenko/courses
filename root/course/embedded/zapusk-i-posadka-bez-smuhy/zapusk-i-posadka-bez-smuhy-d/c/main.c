#include <stdint.h>
#include <stdbool.h>

typedef enum {
    FLIGHT_STATE_IDLE = 0,
    FLIGHT_STATE_TAKEOFF_WAIT_TRIGGER,
    FLIGHT_STATE_TAKEOFF_RAMPUP,
    FLIGHT_STATE_TAKEOFF_CLIMB,
    FLIGHT_STATE_MISSION_NAV,
    FLIGHT_STATE_LAND_APPROACH,
    FLIGHT_STATE_LAND_GLIDESLOPE,
    FLIGHT_STATE_LAND_FLARE,
    FLIGHT_STATE_LAND_TOUCHDOWN,
    FLIGHT_STATE_LAND_ABORT
} flight_fsm_state_t;

typedef struct {
    float accel_launch_threshold_g; /* Поріг стартового перевантаження (2.2g) */
    float safe_climb_alt_m;         /* Безпечна висота завершення зльоту (25.0 м) */
    float flare_alt_m;              /* Висота вирівнювання над землею (1.2 м) */
    float approach_airspeed_ms;     /* Цільова швидкість на глісаді (14.0 м/с) */
    float climb_pitch_deg;          /* Тангаж набору висоти (+14.0°) */
    float flare_pitch_deg;          /* Тангаж вирівнювання (+6.0°) */
} flight_fsm_config_t;

typedef struct {
    float target_pitch_deg;
    float target_roll_deg;
    float throttle_cmd;             /* 0.0 .. 1.0 */
    bool esc_brake_enable;
    bool is_disarmed;
} flight_fsm_output_t;

typedef struct {
    flight_fsm_state_t state;
    flight_fsm_config_t config;
    uint32_t state_timer_ms;
    float current_throttle;
} flight_fsm_t;

void flight_fsm_init(flight_fsm_t *fsm, const flight_fsm_config_t *cfg) {
    fsm->state = FLIGHT_STATE_IDLE;
    fsm->config = *cfg;
    fsm->state_timer_ms = 0;
    fsm->current_throttle = 0.0f;
}

void flight_fsm_start_takeoff(flight_fsm_t *fsm) {
    fsm->state = FLIGHT_STATE_TAKEOFF_WAIT_TRIGGER;
    fsm->state_timer_ms = 0;
    fsm->current_throttle = 0.0f;
}

void flight_fsm_start_landing(flight_fsm_t *fsm) {
    if (fsm->state == FLIGHT_STATE_MISSION_NAV) {
        fsm->state = FLIGHT_STATE_LAND_APPROACH;
        fsm->state_timer_ms = 0;
    }
}

flight_fsm_output_t flight_fsm_update(flight_fsm_t *fsm,
                                      float accel_x_g,
                                      float alt_agl_m,
                                      float airspeed_ms,
                                      bool abort_requested,
                                      uint32_t dt_ms) {
    flight_fsm_output_t out = {
        .target_pitch_deg = 0.0f,
        .target_roll_deg = 0.0f,
        .throttle_cmd = 0.0f,
        .esc_brake_enable = false,
        .is_disarmed = false
    };

    fsm->state_timer_ms += dt_ms;

    switch (fsm->state) {
    case FLIGHT_STATE_IDLE:
        out.is_disarmed = true;
        break;

    case FLIGHT_STATE_TAKEOFF_WAIT_TRIGGER:
        out.target_pitch_deg = fsm->config.climb_pitch_deg;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.0f;
        if (accel_x_g >= fsm->config.accel_launch_threshold_g) {
            fsm->state = FLIGHT_STATE_TAKEOFF_RAMPUP;
            fsm->state_timer_ms = 0;
        }
        break;

    case FLIGHT_STATE_TAKEOFF_RAMPUP:
        out.target_pitch_deg = fsm->config.climb_pitch_deg;
        out.target_roll_deg = 0.0f;
        /* Затримка 250 мс перед набором газу */
        if (fsm->state_timer_ms > 250) {
            fsm->current_throttle += 2.0f * ((float)dt_ms / 1000.0f);
            if (fsm->current_throttle >= 0.90f) {
                fsm->current_throttle = 0.90f;
                fsm->state = FLIGHT_STATE_TAKEOFF_CLIMB;
                fsm->state_timer_ms = 0;
            }
        }
        out.throttle_cmd = fsm->current_throttle;
        break;

    case FLIGHT_STATE_TAKEOFF_CLIMB:
        out.target_pitch_deg = fsm->config.climb_pitch_deg;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.90f;
        if (alt_agl_m >= fsm->config.safe_climb_alt_m) {
            fsm->state = FLIGHT_STATE_MISSION_NAV;
            fsm->state_timer_ms = 0;
        }
        break;

    case FLIGHT_STATE_MISSION_NAV:
        out.target_pitch_deg = 2.0f;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.60f;
        break;

    case FLIGHT_STATE_LAND_APPROACH:
        out.target_pitch_deg = -3.0f; /* Зниження по глісаді */
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = (airspeed_ms < fsm->config.approach_airspeed_ms) ? 0.45f : 0.20f;
        if (alt_agl_m <= 10.0f) {
            fsm->state = FLIGHT_STATE_LAND_GLIDESLOPE;
            fsm->state_timer_ms = 0;
        }
        if (abort_requested) {
            fsm->state = FLIGHT_STATE_LAND_ABORT;
            fsm->state_timer_ms = 0;
        }
        break;

    case FLIGHT_STATE_LAND_GLIDESLOPE:
        out.target_pitch_deg = -3.5f;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.25f;
        if (alt_agl_m <= fsm->config.flare_alt_m) {
            fsm->state = FLIGHT_STATE_LAND_FLARE;
            fsm->state_timer_ms = 0;
        }
        if (abort_requested) {
            fsm->state = FLIGHT_STATE_LAND_ABORT;
            fsm->state_timer_ms = 0;
        }
        break;

    case FLIGHT_STATE_LAND_FLARE:
        out.target_pitch_deg = fsm->config.flare_pitch_deg; /* Вирівнювання носа */
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.0f;
        out.esc_brake_enable = true; /* Активне гальмування пропелера */
        if (alt_agl_m <= 0.2f || fsm->state_timer_ms > 2500) {
            fsm->state = FLIGHT_STATE_LAND_TOUCHDOWN;
            fsm->state_timer_ms = 0;
        }
        break;

    case FLIGHT_STATE_LAND_TOUCHDOWN:
        out.target_pitch_deg = 0.0f;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 0.0f;
        out.esc_brake_enable = true;
        out.is_disarmed = true;
        break;

    case FLIGHT_STATE_LAND_ABORT:
        out.target_pitch_deg = fsm->config.climb_pitch_deg;
        out.target_roll_deg = 0.0f;
        out.throttle_cmd = 1.0f; /* Максимальна тяга для набору */
        if (alt_agl_m >= fsm->config.safe_climb_alt_m) {
            fsm->state = FLIGHT_STATE_MISSION_NAV;
            fsm->state_timer_ms = 0;
        }
        break;
    }

    return out;
}

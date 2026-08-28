#include <stdint.h>
#include <stdbool.h>

typedef enum {
    LAUNCH_STATE_IDLE = 0,
    LAUNCH_STATE_WAIT_ACCEL,
    LAUNCH_STATE_ACCEL_DETECTED,
    LAUNCH_STATE_MOTOR_DELAY,
    LAUNCH_STATE_THROTTLE_RAMP,
    LAUNCH_STATE_FLYING,
    LAUNCH_STATE_ABORTED
} launch_state_t;

typedef struct {
    float accel_threshold_g;     /* Поріг прискорення для детектування (напр. 2.2g) */
    uint32_t accel_time_ms;      /* Мінімальна тривалість перевантаження (напр. 60 мс) */
    uint32_t motor_delay_ms;     /* Захисна затримка до вмикання мотора (напр. 300 мс) */
    uint32_t launch_timeout_ms;  /* Максимальний час виходу на політ (напр. 3000 мс) */
    float throttle_ramp_rate;    /* Швидкість зростання газу (1.0 / секунди) */
    float target_climb_throttle; /* Цільовий рівень газу для набору (напр. 0.85) */
} launch_config_t;

typedef struct {
    launch_state_t state;
    launch_config_t config;
    uint32_t state_timer_ms;
    uint32_t total_launch_timer_ms;
    float current_throttle;
    bool is_armed;
} launch_detector_t;

void launch_detector_init(launch_detector_t *ld, const launch_config_t *cfg) {
    ld->state = LAUNCH_STATE_IDLE;
    ld->config = *cfg;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
    ld->current_throttle = 0.0f;
    ld->is_armed = false;
}

void launch_detector_arm(launch_detector_t *ld) {
    ld->is_armed = true;
    ld->state = LAUNCH_STATE_WAIT_ACCEL;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
    ld->current_throttle = 0.0f;
}

void launch_detector_disarm(launch_detector_t *ld) {
    ld->is_armed = false;
    ld->state = LAUNCH_STATE_IDLE;
    ld->current_throttle = 0.0f;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
}

float launch_detector_update(launch_detector_t *ld, float accel_forward_g, float airspeed_ms, uint32_t dt_ms) {
    if (!ld->is_armed) {
        ld->state = LAUNCH_STATE_IDLE;
        ld->current_throttle = 0.0f;
        return 0.0f;
    }

    if (ld->state != LAUNCH_STATE_IDLE && ld->state != LAUNCH_STATE_WAIT_ACCEL && ld->state != LAUNCH_STATE_FLYING) {
        ld->total_launch_timer_ms += dt_ms;
        if (ld->total_launch_timer_ms > ld->config.launch_timeout_ms) {
            /* Аварійний тайм-аут: літак не набрав швидкість за відведений час */
            ld->state = LAUNCH_STATE_ABORTED;
            ld->current_throttle = 0.0f;
            return 0.0f;
        }
    }

    switch (ld->state) {
    case LAUNCH_STATE_IDLE:
    case LAUNCH_STATE_ABORTED:
        ld->current_throttle = 0.0f;
        break;

    case LAUNCH_STATE_WAIT_ACCEL:
        ld->current_throttle = 0.0f;
        if (accel_forward_g >= ld->config.accel_threshold_g) {
            ld->state = LAUNCH_STATE_ACCEL_DETECTED;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_ACCEL_DETECTED:
        ld->current_throttle = 0.0f;
        ld->state_timer_ms += dt_ms;
        if (accel_forward_g < ld->config.accel_threshold_g * 0.7f) {
            /* Прискорення обірвалося занадто швидко — випадковий поштовх */
            ld->state = LAUNCH_STATE_WAIT_ACCEL;
            ld->state_timer_ms = 0;
        } else if (ld->state_timer_ms >= ld->config.accel_time_ms) {
            /* Стійкий розгін підтверджено — перехід до захисної затримки */
            ld->state = LAUNCH_STATE_MOTOR_DELAY;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_MOTOR_DELAY:
        ld->current_throttle = 0.0f;
        ld->state_timer_ms += dt_ms;
        if (ld->state_timer_ms >= ld->config.motor_delay_ms) {
            ld->state = LAUNCH_STATE_THROTTLE_RAMP;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_THROTTLE_RAMP:
        ld->current_throttle += ld->config.throttle_ramp_rate * ((float)dt_ms / 1000.0f);
        if (ld->current_throttle >= ld->config.target_climb_throttle) {
            ld->current_throttle = ld->config.target_climb_throttle;
            ld->state = LAUNCH_STATE_FLYING;
        }
        break;

    case LAUNCH_STATE_FLYING:
        /* Нормальний політ — газ утримується на цільовому рівні для набору */
        ld->current_throttle = ld->config.target_climb_throttle;
        break;
    }

    return ld->current_throttle;
}

#include <stdint.h>
#include <stdbool.h>

#define HEARTBEAT_TIMEOUT_TICKS  100U  /* Таймаут зв'язку: 100 мс */
#define MOTOR_DERATE_STEP_PCT     10U  /* Крок плавного скидання струму */

typedef enum {
    DRIVE_STATE_INIT = 0,
    DRIVE_STATE_RUNNING,
    DRIVE_STATE_FAULT_DERATING,
    DRIVE_STATE_SAFE_STOP
} drive_state_t;

typedef struct {
    uint32_t last_heartbeat_tick;
    uint32_t current_power_pct;
    drive_state_t state;
    uint32_t fault_code;
} drive_controller_t;

/* Апаратна заглушка керування ШІМ */
extern void hw_motor_set_pwm(uint32_t power_pct);
extern uint32_t hw_get_monotonic_ticks_ms(void);

void drive_controller_init(drive_controller_t *ctrl) {
    ctrl->last_heartbeat_tick = hw_get_monotonic_ticks_ms();
    ctrl->current_power_pct = 0;
    ctrl->state = DRIVE_STATE_INIT;
    ctrl->fault_code = 0;
    hw_motor_set_pwm(0);
}

void drive_controller_feed_heartbeat(drive_controller_t *ctrl) {
    ctrl->last_heartbeat_tick = hw_get_monotonic_ticks_ms();
    if (ctrl->state == DRIVE_STATE_FAULT_DERATING || ctrl->state == DRIVE_STATE_INIT) {
        ctrl->state = DRIVE_STATE_RUNNING;
    }
}

/* Періодичний крок керування (викликається кожні 10 мс) */
void drive_controller_update(drive_controller_t *ctrl, uint32_t target_power_pct) {
    uint32_t now = hw_get_monotonic_ticks_ms();

    /* Безпечна беззнакова перевірка різниці часу (modulo 2^32) */
    uint32_t elapsed = now - ctrl->last_heartbeat_tick;
    bool link_lost = (elapsed > HEARTBEAT_TIMEOUT_TICKS);

    switch (ctrl->state) {
        case DRIVE_STATE_RUNNING:
            if (link_lost) {
                ctrl->state = DRIVE_STATE_FAULT_DERATING;
                ctrl->fault_code = 0xE001; /* Помилка: розрив лінка */
            } else {
                ctrl->current_power_pct = target_power_pct;
                hw_motor_set_pwm(ctrl->current_power_pct);
            }
            break;

        case DRIVE_STATE_FAULT_DERATING:
            /* Плавний спуск струму для усунення індуктивного викиду */
            if (ctrl->current_power_pct > MOTOR_DERATE_STEP_PCT) {
                ctrl->current_power_pct -= MOTOR_DERATE_STEP_PCT;
            } else {
                ctrl->current_power_pct = 0;
                ctrl->state = DRIVE_STATE_SAFE_STOP;
            }
            hw_motor_set_pwm(ctrl->current_power_pct);
            break;

        case DRIVE_STATE_SAFE_STOP:
        case DRIVE_STATE_INIT:
        default:
            hw_motor_set_pwm(0);
            break;
    }
}

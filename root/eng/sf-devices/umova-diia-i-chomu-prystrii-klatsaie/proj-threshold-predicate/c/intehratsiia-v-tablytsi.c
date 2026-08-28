#include <stdio.h>

typedef enum {
    COOLER_STATE_IDLE,
    COOLER_STATE_COOLING,
    COOLER_STATE_ALARM
} cooler_state_t;

typedef struct {
    cooler_state_t state;
    hysteresis_cfg_f32_t fan_hysteresis;
    hysteresis_state_f32_t fan_state;
    float alarm_threshold_c;
} cooler_controller_t;

void cooler_controller_init(cooler_controller_t *ctrl) {
    ctrl->state = COOLER_STATE_IDLE;
    /* Вимкнення кулера при 45°C, увімкнення при 60°C (мертва зона 15°C) */
    ctrl->fan_hysteresis.low_threshold = 45.0f;
    ctrl->fan_hysteresis.high_threshold = 60.0f;
    ctrl->fan_state.current_state = false;
    ctrl->fan_state.initialized = false;
    ctrl->alarm_threshold_c = 85.0f;
}

void cooler_controller_step(cooler_controller_t *ctrl, float temp_c) {
    /* Крок 1: обчислення порогового предикату */
    bool fan_demand = hysteresis_update_f32(&ctrl->fan_hysteresis, &ctrl->fan_state, temp_c);

    /* Крок 2: диспетчеризація станів FSM */
    switch (ctrl->state) {
        case COOLER_STATE_IDLE:
            if (temp_c >= ctrl->alarm_threshold_c) {
                ctrl->state = COOLER_STATE_ALARM;
            } else if (fan_demand) {
                ctrl->state = COOLER_STATE_COOLING;
            }
            break;

        case COOLER_STATE_COOLING:
            if (temp_c >= ctrl->alarm_threshold_c) {
                ctrl->state = COOLER_STATE_ALARM;
            } else if (!fan_demand) {
                ctrl->state = COOLER_STATE_IDLE;
            }
            break;

        case COOLER_STATE_ALARM:
            /* Повернення з аварійного стану лише після повного охолодження */
            if (temp_c < ctrl->fan_hysteresis.low_threshold) {
                ctrl->state = COOLER_STATE_IDLE;
            }
            break;
    }
}

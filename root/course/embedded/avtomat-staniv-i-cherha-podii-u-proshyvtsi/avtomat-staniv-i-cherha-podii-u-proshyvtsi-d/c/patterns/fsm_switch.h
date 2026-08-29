#ifndef EVSE_PATTERN_FSM_SWITCH_H
#define EVSE_PATTERN_FSM_SWITCH_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Патерн 1: вкладений switch-case. Найкоротший шлях від діаграми станів до
 * робочого коду; тримається доти, доки станів менше півдесятка.
 */

typedef enum {
    SW_ST_STANDBY = 0,
    SW_ST_CONNECTED,
    SW_ST_CHARGING,
    SW_ST_FAULT,
    SW_ST_COUNT
} sw_state_t;

typedef enum {
    SW_EV_PLUG_IN = 0,
    SW_EV_AUTH_SUCCESS,
    SW_EV_CHARGE_REQUEST,
    SW_EV_UNPLUG,
    SW_EV_OVERCURRENT,
    SW_EV_RESET_BTN,
    SW_EV_COUNT
} sw_event_t;

typedef struct {
    sw_state_t state;
    bool       authorized;
    bool       lock_engaged;
    uint8_t    current_limit_a;
} sw_fsm_t;

void        sw_fsm_init(sw_fsm_t *fsm, uint8_t current_limit_a);
void        sw_fsm_dispatch(sw_fsm_t *fsm, sw_event_t evt);
const char *sw_state_name(sw_state_t s);

#endif /* EVSE_PATTERN_FSM_SWITCH_H */

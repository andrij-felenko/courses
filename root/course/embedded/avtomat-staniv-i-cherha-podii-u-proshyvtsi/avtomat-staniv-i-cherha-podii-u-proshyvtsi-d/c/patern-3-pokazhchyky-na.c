#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EV_ENTRY,
    EV_EXIT,
    EV_BTN_PRESS,
    EV_TIMER_EXPIRED
} Signal;

typedef struct PumpController PumpController;
typedef void (*StateFn)(PumpController *me, Signal sig);

struct PumpController {
    StateFn state;
    uint32_t fill_level;
};

// Прототипи функцій станів
static void state_draining(PumpController *me, Signal sig);
static void state_filling(PumpController *me, Signal sig);

static void fsm_transition(PumpController *me, StateFn target) {
    if (me->state) me->state(me, EV_EXIT);
    me->state = target;
    if (me->state) me->state(me, EV_ENTRY);
}

static void state_filling(PumpController *me, Signal sig) {
    switch (sig) {
        case EV_ENTRY:
            // GPIO_SetHigh(VALVE_PIN);
            break;
        case EV_EXIT:
            // GPIO_SetLow(VALVE_PIN);
            break;
        case EV_TIMER_EXPIRED:
            fsm_transition(me, state_draining);
            break;
        default:
            break;
    }
}

static void state_draining(PumpController *me, Signal sig) {
    switch (sig) {
        case EV_ENTRY:
            // GPIO_SetHigh(PUMP_PIN);
            break;
        case EV_EXIT:
            // GPIO_SetLow(PUMP_PIN);
            break;
        case EV_BTN_PRESS:
            fsm_transition(me, state_filling);
            break;
        default:
            break;
    }
}

void pump_controller_init(PumpController *me) {
    me->state = NULL;
    me->fill_level = 0;
    fsm_transition(me, state_filling);
}

#include <stdint.h>

typedef enum { S_GREEN, S_YELLOW, S_RED, S_RED_YELLOW } state_t;

static state_t state = S_GREEN;

/* Мур: вихід залежить ЛИШЕ від стану — лампи горять рівно й стабільно */
static void set_lamps(uint8_t r, uint8_t y, uint8_t g) {
    LAMP_RED   = r;
    LAMP_YELLOW = y;
    LAMP_GREEN = g;
}

static void traffic_outputs(state_t s) {
    switch (s) {                 /* R  Y  G */
        case S_GREEN:      set_lamps(0, 0, 1); break;
        case S_YELLOW:     set_lamps(0, 1, 0); break;
        case S_RED:        set_lamps(1, 0, 0); break;
        case S_RED_YELLOW: set_lamps(1, 1, 0); break;
    }
}

/* перехід «по колу за модулем 4» — викликати на кожен tick таймера */
void traffic_on_tick(void) {
    switch (state) {
        case S_GREEN:      state = S_YELLOW;     break;
        case S_YELLOW:     state = S_RED;        break;
        case S_RED:        state = S_RED_YELLOW; break;
        case S_RED_YELLOW: state = S_GREEN;      break;
    }
    traffic_outputs(state);      /* вихід Мура: з нового стану */
}

#include <stdint.h>

typedef enum { LOCKED, OPEN, STATE_COUNT } state_t;
typedef enum { COIN, PUSH, EVENT_COUNT } event_t;

typedef void (*action_fn)(void);   /* дія переходу (модель Мілі) */

typedef struct {
    state_t   next;                /* новий стан */
    action_fn action;             /* що зробити на переході; NULL — нічого */
} cell_t;

/* уся поведінка — тут, як дані; рядок = стан, стовпець = подія */
static const cell_t table[STATE_COUNT][EVENT_COUNT] = {
    /*           COIN                 PUSH               */
    [LOCKED] = { { OPEN,   unlock }, { LOCKED, NULL } },
    [OPEN]   = { { OPEN,   NULL   }, { LOCKED, lock } },
};

static state_t state = LOCKED;

void fsm_dispatch(event_t ev) {
    if (ev >= EVENT_COUNT) {            /* чужа / невалідна подія */
        state = LOCKED;                /* failsafe: безпечний стан турнікета — замкнено */
        return;
    }
    cell_t c = table[state][ev];        /* один індекс — O(1) */
    if (c.action) c.action();          /* дія НА переході — модель Мілі */
    if (c.next != state) {             /* перехід СПРАВДІ змінює стан? */
        on_exit(state);                /* дії «на виході» зі старого… */
        on_enter(c.next);              /* …і «на вході» в новий — модель Мура */
    }
    state = c.next;
}

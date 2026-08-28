#include <stdbool.h>

// Пара «вихід → вхід», з'єднана доріжкою на платі.
typedef struct {
    gpio_pin_t out_pin;
    gpio_pin_t in_pin;
} loop_t;

static const loop_t loops[] = {
    { PIN_LOOP0_OUT, PIN_LOOP0_IN },
    { PIN_LOOP1_OUT, PIN_LOOP1_IN },
    { PIN_LOOP2_OUT, PIN_LOOP2_IN },
};
#define N_LOOPS (sizeof(loops) / sizeof(loops[0]))

// Перевірити одну петлю: 1 має дати 1, 0 має дати 0.
static bool loop_ok(const loop_t *lp) {
    gpio_set(lp->out_pin, 1);
    delay_us(5);                       // дати рівню усталитись на доріжці
    if (gpio_get(lp->in_pin) != 1) return false;

    gpio_set(lp->out_pin, 0);
    delay_us(5);
    if (gpio_get(lp->in_pin) != 0) return false;

    return true;
}

// Пробігти всі петлі; повернути true лише якщо ВСІ цілі.
bool check_all_loops(void) {
    for (unsigned i = 0; i < N_LOOPS; i++) {
        gpio_mode(loops[i].out_pin, GPIO_OUTPUT);
        gpio_mode(loops[i].in_pin,  GPIO_INPUT_PULLDOWN);  // висячий вхід тягнемо в 0
        if (!loop_ok(&loops[i])) return false;
    }
    return true;
}

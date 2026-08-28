/* Файл: button_led_driver.c (C99 / STM32 HAL & Bare-metal style) */
#include <stdint.h>
#include <stdbool.h>

#define DEBOUNCE_TICKS 5  /* 5 викликів по 10 мс = 50 мс стабільності */

typedef enum {
    BUTTON_RELEASED = 0,
    BUTTON_PRESSING,
    BUTTON_HELD,
    BUTTON_RELEASING
} button_state_t;

typedef struct {
    uint8_t raw_pin_state;
    uint8_t stable_state;
    uint8_t counter;
    button_state_t fsm_state;
} button_t;

void button_init(button_t *btn) {
    btn->raw_pin_state = 1;  /* Активний нуль: за замовчуванням підтяжка в 1 */
    btn->stable_state = 1;
    btn->counter = 0;
    btn->fsm_state = BUTTON_RELEASED;
}

/* Викликається періодично кожні 10 мс із системного таймера SysTick */
bool button_update(button_t *btn, uint8_t current_pin_level) {
    bool event_pressed = false;

    if (current_pin_level != btn->raw_pin_state) {
        btn->raw_pin_state = current_pin_level;
        btn->counter = 0;
    } else {
        if (btn->counter < DEBOUNCE_TICKS) {
            btn->counter++;
            if (btn->counter == DEBOUNCE_TICKS) {
                btn->stable_state = btn->raw_pin_state;
                /* Стан стабілізувався: фіксуємо фронт натискання */
                if (btn->stable_state == 0 && btn->fsm_state == BUTTON_RELEASED) {
                    btn->fsm_state = BUTTON_HELD;
                    event_pressed = true;
                } else if (btn->stable_state == 1) {
                    btn->fsm_state = BUTTON_RELEASED;
                }
            }
        }
    }
    return event_pressed;
}

#include "debounce.h"

/* Кнопка ввімкнена на землю й підтягнута вгору: натиснуто — це логічний нуль. */
#define LEVEL_PRESSED 0U

void button_init(button_t *btn, uint8_t idle_level)
{
    btn->counter = 0U;
    btn->state = (idle_level == LEVEL_PRESSED) ? BUTTON_ST_HELD : BUTTON_ST_RELEASED;
}

button_event_t button_update(button_t *btn, uint8_t pin_level)
{
    const uint8_t pressed = (pin_level == LEVEL_PRESSED) ? 1U : 0U;

    switch (btn->state) {
    case BUTTON_ST_RELEASED:
        if (pressed) {
            btn->state = BUTTON_ST_DEBOUNCE_PRESS;
            btn->counter = 1U;
        }
        break;

    case BUTTON_ST_DEBOUNCE_PRESS:
        if (!pressed) {
            /* Рівень не протримався: це був брязкіт або мережеве наведення на
               високоомний вхід. Лічильник у нуль, автомат назад у спокій. */
            btn->state = BUTTON_ST_RELEASED;
            btn->counter = 0U;
        } else if (++btn->counter >= DEBOUNCE_TICKS) {
            btn->state = BUTTON_ST_HELD;
            btn->counter = 0U;
            return BUTTON_EVENT_PRESSED;
        }
        break;

    case BUTTON_ST_HELD:
        if (!pressed) {
            btn->state = BUTTON_ST_DEBOUNCE_RELEASE;
            btn->counter = 1U;
        }
        break;

    case BUTTON_ST_DEBOUNCE_RELEASE:
        if (pressed) {
            /* Брязкіт на відпусканні симетричний брязкоту на натисканні. */
            btn->state = BUTTON_ST_HELD;
            btn->counter = 0U;
        } else if (++btn->counter >= DEBOUNCE_TICKS) {
            btn->state = BUTTON_ST_RELEASED;
            btn->counter = 0U;
            return BUTTON_EVENT_RELEASED;
        }
        break;

    default:
        /* Структуру побив хтось сторонній — повертаємось у відомий стан. */
        btn->state = BUTTON_ST_RELEASED;
        btn->counter = 0U;
        break;
    }

    return BUTTON_EVENT_NONE;
}

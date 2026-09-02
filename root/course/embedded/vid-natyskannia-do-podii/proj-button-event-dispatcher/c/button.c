#include <stddef.h>

#include "button.h"

/* Історія — зсувний регістр: одиниця це вибірка «відпущено», нуль —
   «натиснуто». Вісім однакових вибірок поспіль (0xFF або 0x00) означають
   стабільний рівень; при тіку 5 мс це 40 мс тиші — довше за брязкіт
   будь-якої тактової кнопки. */

static bool emit(event_queue_t *q, uint8_t id, event_type_t type, uint16_t duration_ms) {
    input_event_t evt;
    evt.id = id;
    evt.type = type;
    evt.duration_ms = duration_ms;
    return queue_push(q, evt);
}

/* Насичене додавання: утримання довше за 65 секунд не повинно обернути
   лічильник на нуль і вдати коротке натискання. */
static uint16_t add_ms(uint16_t base, uint16_t delta) {
    const uint32_t sum = (uint32_t)base + (uint32_t)delta;
    return (sum > UINT16_MAX) ? UINT16_MAX : (uint16_t)sum;
}

/* Розгін автоповтору: лінійно від BTN_REPEAT_SLOW_MS одразу після порогу
   утримання до BTN_REPEAT_FAST_MS на BTN_REPEAT_FULL_SPEED_MS. Саме це дає
   плавне перемотування меню від 0 до 1000 одним натисканням. */
static uint16_t repeat_interval_ms(uint16_t held_ms) {
    if (held_ms <= BTN_LONG_PRESS_MS) {
        return BTN_REPEAT_SLOW_MS;
    }
    if (held_ms >= BTN_REPEAT_FULL_SPEED_MS) {
        return BTN_REPEAT_FAST_MS;
    }
    const uint32_t span = BTN_REPEAT_FULL_SPEED_MS - BTN_LONG_PRESS_MS;
    const uint32_t past = (uint32_t)held_ms - BTN_LONG_PRESS_MS;
    const uint32_t drop = (uint32_t)(BTN_REPEAT_SLOW_MS - BTN_REPEAT_FAST_MS) * past / span;
    return (uint16_t)(BTN_REPEAT_SLOW_MS - drop);
}

bool button_init(button_t *btn, uint8_t id, pin_read_fn read_pin) {
    if (btn == NULL || read_pin == NULL) {
        return false;
    }
    btn->id = id;
    btn->read_pin = read_pin;
    btn->state = BTN_STATE_IDLE;
    btn->timer_ms = 0;
    btn->press_duration_ms = 0;
    btn->gap_ms = 0;
    btn->debounce_history = 0xFFu;  /* стартуємо з «відпущено» */
    btn->long_fired = false;
    btn->no_click = false;
    btn->second_press = false;
    return true;
}

void button_process_tick(button_t *btn, uint16_t tick_ms, event_queue_t *q) {
    if (btn == NULL || q == NULL) {
        return;
    }

    const uint8_t raw = btn->read_pin() ? 1u : 0u;
    btn->debounce_history = (uint8_t)((btn->debounce_history << 1) | raw);

    const bool stable_pressed  = (btn->debounce_history == 0x00u);
    const bool stable_released = (btn->debounce_history == 0xFFu);

    btn->timer_ms = add_ms(btn->timer_ms, tick_ms);

    switch (btn->state) {
    case BTN_STATE_IDLE:
        /* Перший же нуль лише ЗАПУСКАЄ перевірку — подій тут ще немає. */
        if (raw == 0u) {
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        }
        break;

    case BTN_STATE_DEBOUNCING_PRESS:
        if (stable_pressed) {
            /* Дебаунс теж був утриманням — не втрачаємо ці 40 мс. */
            btn->press_duration_ms = btn->timer_ms;
            btn->timer_ms = 0;
            btn->long_fired = false;
            btn->state = BTN_STATE_PRESSED;
            emit(q, btn->id, EVENT_BUTTON_PRESS, 0);
            if (btn->second_press) {
                emit(q, btn->id, EVENT_BUTTON_DOUBLE_CLICK, btn->gap_ms);
                btn->second_press = false;
                btn->no_click = true;  /* після подвійного одинарного не буде */
            }
        } else if (stable_released || btn->timer_ms > BTN_DEBOUNCE_TIMEOUT_MS) {
            /* Стабільного нуля так і не дочекалися: наведення чи одиничний
               імпульс на довгому дроті — натисканням це не вважаємо. */
            btn->state = BTN_STATE_IDLE;
            btn->second_press = false;
        }
        break;

    case BTN_STATE_PRESSED:
        btn->press_duration_ms = add_ms(btn->press_duration_ms, tick_ms);
        if (raw == 1u) {
            btn->state = BTN_STATE_DEBOUNCING_RELEASE;
            btn->timer_ms = 0;
        } else if (!btn->long_fired && btn->press_duration_ms >= BTN_LONG_PRESS_MS) {
            btn->long_fired = true;
            btn->no_click = true;
            btn->state = BTN_STATE_LONG_PRESS;
            btn->timer_ms = 0;
            emit(q, btn->id, EVENT_BUTTON_LONG_PRESS_START, btn->press_duration_ms);
        }
        break;

    case BTN_STATE_DEBOUNCING_RELEASE:
        btn->press_duration_ms = add_ms(btn->press_duration_ms, tick_ms);
        if (stable_released) {
            emit(q, btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms);
            if (btn->no_click) {
                btn->no_click = false;
                btn->long_fired = false;
                btn->state = BTN_STATE_IDLE;
            } else {
                btn->state = BTN_STATE_WAIT_DOUBLE_CLICK;
                btn->timer_ms = 0;
            }
        } else if (stable_pressed) {
            /* Контакт замкнувся назад — це був брязкіт розмикання, а не
               відпускання. Повертаємось туди, звідки прийшли. */
            btn->state = btn->long_fired ? BTN_STATE_REPEAT : BTN_STATE_PRESSED;
            btn->timer_ms = 0;
        }
        break;

    case BTN_STATE_WAIT_DOUBLE_CLICK:
        if (raw == 0u) {
            btn->gap_ms = btn->timer_ms;
            btn->second_press = true;
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        } else if (btn->timer_ms >= BTN_DOUBLE_CLICK_MS) {
            /* Вікно минуло — аж тепер клік одинарний. Саме ця затримка і є
               ціна подвійного кліку в інтерфейсі. */
            emit(q, btn->id, EVENT_BUTTON_SHORT_CLICK, btn->press_duration_ms);
            btn->state = BTN_STATE_IDLE;
        }
        break;

    case BTN_STATE_LONG_PRESS:
        btn->press_duration_ms = add_ms(btn->press_duration_ms, tick_ms);
        if (raw == 1u) {
            btn->state = BTN_STATE_DEBOUNCING_RELEASE;
            btn->timer_ms = 0;
        } else if (btn->timer_ms >= BTN_HOLD_REPORT_MS) {
            btn->timer_ms = 0;
            btn->state = BTN_STATE_REPEAT;
            emit(q, btn->id, EVENT_BUTTON_LONG_PRESS_HOLD, btn->press_duration_ms);
        }
        break;

    case BTN_STATE_REPEAT:
        btn->press_duration_ms = add_ms(btn->press_duration_ms, tick_ms);
        if (raw == 1u) {
            btn->state = BTN_STATE_DEBOUNCING_RELEASE;
            btn->timer_ms = 0;
        } else if (btn->timer_ms >= repeat_interval_ms(btn->press_duration_ms)) {
            btn->timer_ms = 0;
            emit(q, btn->id, EVENT_BUTTON_REPEAT, btn->press_duration_ms);
        }
        break;

    default:
        /* Пам'ять зіпсовано чи структуру не ініціалізовано — тихо повертаємось
           у визначений стан, а не блукаємо по таблиці переходів. */
        btn->state = BTN_STATE_IDLE;
        break;
    }
}

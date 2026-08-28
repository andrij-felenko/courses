#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Події неінвазивного інтерфейсу */
typedef enum {
    EVT_NONE = 0,
    EVT_REED_SHORT_TAP,
    EVT_REED_LONG_HOLD,
    EVT_TOUCH_PRESS,
    EVT_TOUCH_RELEASE
} InterfaceEvent;

/* Режими анімації світловода */
typedef enum {
    LED_MODE_OFF = 0,
    LED_MODE_STATIC,
    LED_MODE_HEARTBEAT,
    LED_MODE_BLINK_FAST
} LedMode;

/* Конфігурація часових параметрів (у мілісекундах) */
#define DEBOUNCE_TIME_MS      30
#define LONG_HOLD_TIME_MS     5000
#define TOUCH_HYSTERESIS      120
#define BASELINE_ALPHA_SHIFT  6     /* Фільтр IIR: коефіцієнт 1/64 для повільного дрейфу */

/* Структура стану магнітного сенсора (геркон / Холл) */
typedef struct {
    bool raw_state;
    bool debounced_state;
    uint32_t last_edge_time_ms;
    uint32_t press_start_time_ms;
    bool long_hold_triggered;
} MagneticSensor;

/* Структура ємнісного сенсора дотику */
typedef struct {
    uint32_t baseline_fixed;  /* Опорне значення у форматі з фіксованою точкою Q16.16 */
    bool is_touched;
    uint32_t touch_debounce_time_ms;
} TouchSensor;

/* Структура індикатора світловода */
typedef struct {
    LedMode mode;
    uint8_t current_brightness;
    uint8_t target_brightness;
    uint16_t phase_counter;
} LightPipeIndicator;

/* Головний контекст контролера */
typedef struct {
    MagneticSensor reed;
    TouchSensor touch;
    LightPipeIndicator led;
    void (*event_callback)(InterfaceEvent event);
} SealedInterfaceController;

/* Ініціалізація підсистеми */
void sealed_interface_init(SealedInterfaceController *ctrl, void (*cb)(InterfaceEvent)) {
    if (!ctrl) return;
    ctrl->event_callback = cb;

    ctrl->reed.raw_state = false;
    ctrl->reed.debounced_state = false;
    ctrl->reed.last_edge_time_ms = 0;
    ctrl->reed.press_start_time_ms = 0;
    ctrl->reed.long_hold_triggered = false;

    ctrl->touch.baseline_fixed = 0;
    ctrl->touch.is_touched = false;
    ctrl->touch.touch_debounce_time_ms = 0;

    ctrl->led.mode = LED_MODE_OFF;
    ctrl->led.current_brightness = 0;
    ctrl->led.target_brightness = 0;
    ctrl->led.phase_counter = 0;
}

/* Оновлення стану магнітного сенсора (викликається в циклі або по таймеру) */
static void update_magnetic(SealedInterfaceController *ctrl, bool pin_level, uint32_t now_ms) {
    MagneticSensor *m = &ctrl->reed;

    /* Виявлення перепаду */
    if (pin_level != m->raw_state) {
        m->raw_state = pin_level;
        m->last_edge_time_ms = now_ms;
    }

    /* Антидеренчання за часовим вікном */
    if ((now_ms - m->last_edge_time_ms) >= DEBOUNCE_TIME_MS) {
        if (m->raw_state != m->debounced_state) {
            m->debounced_state = m->raw_state;

            if (m->debounced_state) {
                /* Замикання контакту під дією магніту */
                m->press_start_time_ms = now_ms;
                m->long_hold_triggered = false;
            } else {
                /* Розмикання контакту */
                if (!m->long_hold_triggered && (now_ms - m->press_start_time_ms) >= DEBOUNCE_TIME_MS) {
                    if (ctrl->event_callback) {
                        ctrl->event_callback(EVT_REED_SHORT_TAP);
                    }
                }
            }
        }
    }

    /* Перевірка тривалого сервісного утримання (5 секунд) */
    if (m->debounced_state && !m->long_hold_triggered) {
        if ((now_ms - m->press_start_time_ms) >= LONG_HOLD_TIME_MS) {
            m->long_hold_triggered = true;
            if (ctrl->event_callback) {
                ctrl->event_callback(EVT_REED_LONG_HOLD);
            }
        }
    }
}

/* Оновлення ємнісного сенсора з адаптивним фільтром базової лінії */
static void update_capacitive(SealedInterfaceController *ctrl, uint16_t raw_counts, uint32_t now_ms) {
    TouchSensor *t = &ctrl->touch;

    /* Початкова ініціалізація базової лінії */
    if (t->baseline_fixed == 0) {
        t->baseline_fixed = (uint32_t)raw_counts << 16;
        return;
    }

    uint16_t baseline_val = (uint16_t)(t->baseline_fixed >> 16);
    int32_t delta = (int32_t)raw_counts - (int32_t)baseline_val;

    /* Якщо сигнал вищий за поріг — маємо дотик */
    bool touched_raw = (delta > TOUCH_HYSTERESIS);

    if (touched_raw != t->is_touched) {
        if (t->touch_debounce_time_ms == 0) {
            t->touch_debounce_time_ms = now_ms;
        } else if ((now_ms - t->touch_debounce_time_ms) >= DEBOUNCE_TIME_MS) {
            t->is_touched = touched_raw;
            t->touch_debounce_time_ms = 0;
            if (ctrl->event_callback) {
                ctrl->event_callback(t->is_touched ? EVT_TOUCH_PRESS : EVT_TOUCH_RELEASE);
            }
        }
    } else {
        t->touch_debounce_time_ms = 0;
    }

    /* Оновлюємо базову лінію ТІЛЬКИ коли кнопка відпущена, щоб уникнути захоплення дотику в базу */
    if (!t->is_touched) {
        /* IIR-фільтр низьких частот: baseline += (raw - baseline) / 64 */
        int32_t error = ((int32_t)raw_counts << 16) - (int32_t)t->baseline_fixed;
        t->baseline_fixed += (error >> BASELINE_ALPHA_SHIFT);
    }
}

/* Оновлення генератора анімації світловода */
static void update_indicator(SealedInterfaceController *ctrl) {
    LightPipeIndicator *ind = &ctrl->led;
    ind->phase_counter++;

    switch (ind->mode) {
        case LED_MODE_OFF:
            ind->current_brightness = 0;
            break;

        case LED_MODE_STATIC:
            ind->current_brightness = ind->target_brightness;
            break;

        case LED_MODE_HEARTBEAT: {
            /* Формування плавного дихання через трикутну фазу */
            uint16_t step = ind->phase_counter % 256;
            if (step < 128) {
                ind->current_brightness = (uint8_t)(step * 2);
            } else {
                ind->current_brightness = (uint8_t)((255 - step) * 2);
            }
            break;
        }

        case LED_MODE_BLINK_FAST:
            ind->current_brightness = ((ind->phase_counter % 32) < 16) ? 255 : 0;
            break;
    }
}

/* Головний такт обробки інтерфейсу (виклик кожні 10 мс) */
void sealed_interface_tick(SealedInterfaceController *ctrl, bool reed_raw_pin, uint16_t touch_raw_counts, uint32_t now_ms) {
    if (!ctrl) return;
    update_magnetic(ctrl, reed_raw_pin, now_ms);
    update_capacitive(ctrl, touch_raw_counts, now_ms);
    update_indicator(ctrl);
}

/* Отримання поточного значення ШІМ для виводу на таймер світлодіода */
uint8_t sealed_interface_get_led_pwm(const SealedInterfaceController *ctrl) {
    return ctrl ? ctrl->led.current_brightness : 0;
}

void sealed_interface_set_led_mode(SealedInterfaceController *ctrl, LedMode mode, uint8_t max_brightness) {
    if (!ctrl) return;
    ctrl->led.mode = mode;
    ctrl->led.target_brightness = max_brightness;
}

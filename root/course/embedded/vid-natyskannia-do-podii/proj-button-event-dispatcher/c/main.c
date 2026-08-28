#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_SIZE 16

typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESS,
    EVENT_BUTTON_RELEASE,
    EVENT_BUTTON_SHORT_CLICK,
    EVENT_BUTTON_DOUBLE_CLICK,
    EVENT_BUTTON_LONG_PRESS_START,
    EVENT_BUTTON_LONG_PRESS_HOLD,
    EVENT_BUTTON_REPEAT,
    EVENT_ENCODER_CW,
    EVENT_ENCODER_CCW
} event_type_t;

typedef struct {
    uint8_t id;
    event_type_t type;
    uint16_t duration_ms;
} input_event_t;

/* --- Кільцева черга подій FIFO --- */
typedef struct {
    input_event_t buffer[EVENT_QUEUE_SIZE];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
} event_queue_t;

void queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

bool queue_push(event_queue_t *q, input_event_t evt) {
    if (q->count >= EVENT_QUEUE_SIZE) {
        return false; /* Переповнення буфера: нова подія відкидається */
    }
    q->buffer[q->head] = evt;
    q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_SIZE);
    q->count++;
    return true;
}

bool queue_pop(event_queue_t *q, input_event_t *evt) {
    if (q->count == 0) {
        return false;
    }
    *evt = q->buffer[q->tail];
    q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_SIZE);
    q->count--;
    return true;
}

/* --- Скінченний автомат кнопки --- */
typedef enum {
    BTN_STATE_IDLE,
    BTN_STATE_DEBOUNCING_PRESS,
    BTN_STATE_PRESSED,
    BTN_STATE_DEBOUNCING_RELEASE,
    BTN_STATE_WAIT_DOUBLE_CLICK,
    BTN_STATE_LONG_PRESS,
    BTN_STATE_REPEAT
} btn_fsm_state_t;

typedef struct {
    uint8_t id;
    uint8_t (*read_pin)(void);  /* Повертає 0 (натиснуто, active-low) або 1 (відпущено) */
    btn_fsm_state_t state;
    uint16_t timer_ms;
    uint16_t press_duration_ms;
    uint8_t debounce_history;
} button_t;

void button_init(button_t *btn, uint8_t id, uint8_t (*read_pin_fn)(void)) {
    btn->id = id;
    btn->read_pin = read_pin_fn;
    btn->state = BTN_STATE_IDLE;
    btn->timer_ms = 0;
    btn->press_duration_ms = 0;
    btn->debounce_history = 0xFF;
}

void button_process_tick(button_t *btn, uint16_t tick_ms, event_queue_t *q) {
    uint8_t raw = btn->read_pin() ? 1 : 0;
    btn->debounce_history = (uint8_t)((btn->debounce_history << 1) | raw);
    bool is_pressed = (btn->debounce_history == 0x00);
    bool is_released = (btn->debounce_history == 0xFF);

    switch (btn->state) {
    case BTN_STATE_IDLE:
        if (raw == 0) {
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        }
        break;

    case BTN_STATE_DEBOUNCING_PRESS:
        btn->timer_ms += tick_ms;
        if (is_pressed) {
            btn->state = BTN_STATE_PRESSED;
            btn->press_duration_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_PRESS, 0});
        } else if (btn->timer_ms > 30) {
            btn->state = BTN_STATE_IDLE;
        }
        break;

    case BTN_STATE_PRESSED:
        btn->press_duration_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_DEBOUNCING_RELEASE;
            btn->timer_ms = 0;
        } else if (btn->press_duration_ms >= 800) {
            btn->state = BTN_STATE_LONG_PRESS;
            btn->timer_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_LONG_PRESS_START, btn->press_duration_ms});
        }
        break;

    case BTN_STATE_DEBOUNCING_RELEASE:
        btn->timer_ms += tick_ms;
        if (is_released) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
            btn->state = BTN_STATE_WAIT_DOUBLE_CLICK;
            btn->timer_ms = 0;
        } else if (btn->timer_ms > 30) {
            btn->state = BTN_STATE_PRESSED;
        }
        break;

    case BTN_STATE_WAIT_DOUBLE_CLICK:
        btn->timer_ms += tick_ms;
        if (raw == 0) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_DOUBLE_CLICK, btn->timer_ms});
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        } else if (btn->timer_ms >= 250) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_SHORT_CLICK, btn->press_duration_ms});
            btn->state = BTN_STATE_IDLE;
        }
        break;

    case BTN_STATE_LONG_PRESS:
        btn->press_duration_ms += tick_ms;
        btn->timer_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_IDLE;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
        } else if (btn->timer_ms >= 100) {
            btn->timer_ms = 0;
            btn->state = BTN_STATE_REPEAT;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_LONG_PRESS_HOLD, btn->press_duration_ms});
        }
        break;

    case BTN_STATE_REPEAT:
        btn->press_duration_ms += tick_ms;
        btn->timer_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_IDLE;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
        } else if (btn->timer_ms >= 80) {
            btn->timer_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_REPEAT, btn->press_duration_ms});
        }
        break;
    }
}

/* --- Декодер квадратурного енкодера --- */
typedef struct {
    uint8_t id;
    uint8_t (*read_phase_a)(void);
    uint8_t (*read_phase_b)(void);
    uint8_t prev_state;
    int8_t sub_step_acc;
} encoder_t;

static const int8_t encoder_lut[16] = {
     0, -1,  1,  0,
     1,  0,  0, -1,
    -1,  0,  0,  1,
     0,  1, -1,  0
};

void encoder_init(encoder_t *enc, uint8_t id, uint8_t (*read_a)(void), uint8_t (*read_b)(void)) {
    enc->id = id;
    enc->read_phase_a = read_a;
    enc->read_phase_b = read_b;
    uint8_t a = enc->read_phase_a() ? 1 : 0;
    uint8_t b = enc->read_phase_b() ? 1 : 0;
    enc->prev_state = (uint8_t)((a << 1) | b);
    enc->sub_step_acc = 0;
}

void encoder_process_tick(encoder_t *enc, event_queue_t *q) {
    uint8_t a = enc->read_phase_a() ? 1 : 0;
    uint8_t b = enc->read_phase_b() ? 1 : 0;
    uint8_t curr = (uint8_t)((a << 1) | b);

    if (curr == enc->prev_state) {
        return;
    }

    uint8_t code = (uint8_t)((enc->prev_state << 2) | curr);
    int8_t step = encoder_lut[code];
    enc->prev_state = curr;

    if (step != 0) {
        enc->sub_step_acc += step;
        if (enc->sub_step_acc >= 4) {
            enc->sub_step_acc = 0;
            queue_push(q, (input_event_t){enc->id, EVENT_ENCODER_CW, 1});
        } else if (enc->sub_step_acc <= -4) {
            enc->sub_step_acc = 0;
            queue_push(q, (input_event_t){enc->id, EVENT_ENCODER_CCW, 1});
        }
    }
}

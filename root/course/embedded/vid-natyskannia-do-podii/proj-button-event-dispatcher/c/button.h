#ifndef BUTTON_H
#define BUTTON_H

#include <stdbool.h>
#include <stdint.h>

#include "event_queue.h"

/* Пороги автомата в мілісекундах. Тік дискретизації — 5 мс. */
#define BTN_DEBOUNCE_TIMEOUT_MS   60u   /* довше за 8 вибірок історії: регістр
                                           має встигнути заповнитися */
#define BTN_LONG_PRESS_MS        800u
#define BTN_DOUBLE_CLICK_MS      250u
#define BTN_HOLD_REPORT_MS       100u   /* пауза між START і першим HOLD */
#define BTN_REPEAT_SLOW_MS       100u   /* темп автоповтору на початку */
#define BTN_REPEAT_FAST_MS        20u   /* темп автоповтору на розгоні */
#define BTN_REPEAT_FULL_SPEED_MS 3000u  /* утримання, після якого темп максимальний */

typedef enum {
    BTN_STATE_IDLE,
    BTN_STATE_DEBOUNCING_PRESS,
    BTN_STATE_PRESSED,
    BTN_STATE_DEBOUNCING_RELEASE,
    BTN_STATE_WAIT_DOUBLE_CLICK,
    BTN_STATE_LONG_PRESS,
    BTN_STATE_REPEAT
} btn_fsm_state_t;

/* Повертає СИРИЙ рівень на піні: 1 — високий (кнопка відпущена, active-low),
   0 — низький. Ніякої фільтрації всередині: фільтрує автомат. */
typedef uint8_t (*pin_read_fn)(void);

typedef struct {
    uint8_t         id;
    pin_read_fn     read_pin;
    btn_fsm_state_t state;
    uint16_t        timer_ms;           /* час у поточному стані */
    uint16_t        press_duration_ms;  /* тривалість поточного утримання */
    uint16_t        gap_ms;             /* пауза між відпусканням і повторним натисканням */
    uint8_t         debounce_history;   /* зсувний регістр 8 останніх вибірок */
    bool            long_fired;         /* LONG_PRESS_START уже видано */
    bool            no_click;           /* при відпусканні кліку не буде */
    bool            second_press;       /* поточне натискання — друге в парі */
} button_t;

bool button_init(button_t *btn, uint8_t id, pin_read_fn read_pin);

/* Викликається з переривання системного таймера рівно раз на тік.
   tick_ms передається явно: якщо таймер плаває через пріоритетніші
   переривання, автомат усе одно міряє час, а не тіки. */
void button_process_tick(button_t *btn, uint16_t tick_ms, event_queue_t *q);

#endif /* BUTTON_H */

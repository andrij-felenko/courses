// cc_reader.h — читач рівня USB-C CC: усереднення, гістерезис, дебаунс,
//               вибір активної лінії CC1/CC2, події під'єднання/від'єднання.
#ifndef CC_READER_H
#define CC_READER_H

#include <stdint.h>
#include <stdbool.h>

// Рівень дозволеного струму, який джерело виставило опором Rp на CC.
typedef enum {
    CC_NONE = 0,   // джерела нема (лінія висить)
    CC_DEFAULT,    // звичайний USB: 0.5 / 0.9 А
    CC_1A5,        // 1.5 А  @ 5 В
    CC_3A0         // 3.0 А  @ 5 В  (15 Вт)
} cc_level_t;

// Яка лінія виявилась активною (куди джерело підтягнуло Rp).
typedef enum { CC_LINE_NONE = 0, CC_LINE_1, CC_LINE_2 } cc_line_t;

// Подія, яку модуль віддає назовні через callback.
typedef enum {
    CC_EV_ATTACHED,   // джерело з'явилось, рівень устоявся й дійсний
    CC_EV_DETACHED,   // джерело зникло (висмикнули кабель чи просів CC)
    CC_EV_LEVEL       // рівень змінився, лишаючись під'єднаним (переуклали)
} cc_event_t;

// Callback викликається з контексту poll() — отже, НЕ з переривання.
typedef void (*cc_cb_t)(cc_event_t ev, cc_level_t level, void *user);

// Як читати дві ноги CC: даємо модулю функцію вимірювання в мілівольтах.
// Так драйвер не прив'язаний до конкретного АЦП (STM32, ESP32, будь-що).
typedef struct {
    uint16_t (*read_mv)(cc_line_t line);  // виміряти CC1 або CC2 у мВ
    cc_cb_t  on_event;                     // подія (може бути NULL)
    void    *user;                         // довільний контекст у callback
} cc_reader_cfg_t;

void       cc_reader_init(const cc_reader_cfg_t *cfg);
void       cc_reader_poll(void);          // звати періодично, ~раз на 1–5 мс
cc_level_t cc_reader_level(void);         // поточний сталий рівень
cc_line_t  cc_reader_active(void);        // активна лінія (для орієнтації CC)
bool       cc_reader_attached(void);      // чи є дійсне під'єднання зараз

#endif

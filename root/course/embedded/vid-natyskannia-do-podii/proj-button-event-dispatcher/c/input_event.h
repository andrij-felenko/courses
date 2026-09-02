#ifndef INPUT_EVENT_H
#define INPUT_EVENT_H

#include <stdint.h>

/* Семантика введення, а не стан пінів: далі по системі ніхто вже не знає,
   що подія народилася з механічного контакту. */
typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESS,             /* контакт замкнувся й рівень стабільний */
    EVENT_BUTTON_RELEASE,           /* контакт розімкнувся й рівень стабільний */
    EVENT_BUTTON_SHORT_CLICK,       /* натиснули й відпустили, другого не було */
    EVENT_BUTTON_DOUBLE_CLICK,      /* друге натискання вкладеться у вікно */
    EVENT_BUTTON_LONG_PRESS_START,  /* утримання перетнуло поріг */
    EVENT_BUTTON_LONG_PRESS_HOLD,   /* утримання триває */
    EVENT_BUTTON_REPEAT,            /* автоповтор із розгоном */
    EVENT_ENCODER_CW,               /* один клац за годинниковою */
    EVENT_ENCODER_CCW               /* один клац проти годинникової */
} event_type_t;

/* Маленька POD-структура: у чергу копіюється одним присвоєнням, без
   покажчиків усередину — інакше споживач читав би вже перезаписану пам'ять. */
typedef struct {
    uint8_t      id;           /* номер органа введення */
    event_type_t type;
    uint16_t     duration_ms;  /* тривалість утримання або пауза між кліками */
} input_event_t;

#endif /* INPUT_EVENT_H */

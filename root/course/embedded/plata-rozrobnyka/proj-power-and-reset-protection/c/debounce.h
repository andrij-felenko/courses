/* Періодичне опитування: кінцевий автомат, який віддає подію лише тоді, коли
   рівень на ніжці протримався незмінним кілька опитувань поспіль. Апаратури не
   торкається взагалі — рівень йому передають ззовні, тож автомат можна ганяти
   на столі звичайним юніт-тестом. */
#ifndef DEBOUNCE_H
#define DEBOUNCE_H

#include <stdint.h>

/* Період опитування 10 мс, п'ять тиків = 50 мс стабільності. Це з запасом
   перекриває 10–20 мс брязкоту контактної пластини. */
#define DEBOUNCE_TICKS 5U

typedef enum {
    BUTTON_EVENT_NONE = 0,
    BUTTON_EVENT_PRESSED,
    BUTTON_EVENT_RELEASED
} button_event_t;

typedef enum {
    BUTTON_ST_RELEASED = 0,
    BUTTON_ST_DEBOUNCE_PRESS,
    BUTTON_ST_HELD,
    BUTTON_ST_DEBOUNCE_RELEASE
} button_state_t;

typedef struct {
    button_state_t state;
    uint8_t counter;  /* скільки опитувань поспіль рівень тримається новим */
} button_t;

/* idle_level — рівень на ніжці в момент старту: якщо кнопку тримають від
   увімкнення живлення, автомат не має видати фальшивого натискання. */
void button_init(button_t *btn, uint8_t idle_level);

/* Викликається строго періодично, раз на 10 мс. */
button_event_t button_update(button_t *btn, uint8_t pin_level);

#endif /* DEBOUNCE_H */

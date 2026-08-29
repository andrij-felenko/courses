#ifndef FM_DEBOUNCE_H
#define FM_DEBOUNCE_H

#include <stdbool.h>
#include <stdint.h>

/* Асиметричний фільтр деренчання. Умови борту (HDOP, інновації EKF, контакт із
   ґрунтом) балансують на межі порога й миготять з частотою такту; автомат мусить
   бачити стійкий стан, а не миготіння.

   Асиметрія навмисна: перехід у бік ДОЗВОЛУ вимагає витримки rise_ms, перехід у
   бік ЗАБОРОНИ — витримки fall_ms, і для охоронців fall_ms дорівнює нулю.
   Небезпеку визнаємо миттєво, безпеку — лише витриману. */
typedef struct {
    bool     state;            /* поточний стійкий стан                        */
    bool     candidate;        /* стан, який чекає на витримку                 */
    uint32_t cand_since_ms;    /* коли кандидат зʼявився                       */
    uint32_t state_since_ms;   /* коли стійкий стан востаннє змінився          */
    bool     primed;           /* фільтр уже бачив хоч один такт               */
} fm_debounce_t;

/* Початкове значення: state = candidate = initial, витримка не триває. */
void fm_debounce_init(fm_debounce_t *d, bool initial);

/* Один такт фільтра. Повертає стійкий стан ПІСЛЯ оновлення. */
bool fm_debounce_update(fm_debounce_t *d, bool raw, uint32_t now_ms,
                        uint32_t rise_ms, uint32_t fall_ms);

/* Скільки мілісекунд поточний стійкий стан уже тримається. */
uint32_t fm_debounce_held_ms(const fm_debounce_t *d, uint32_t now_ms);

static inline bool fm_debounce_state(const fm_debounce_t *d)
{
    return d && d->state;
}

#endif /* FM_DEBOUNCE_H */

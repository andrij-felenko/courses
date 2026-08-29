#ifndef SAFETY_H
#define SAFETY_H

/* Наглядач контуру: зводить докупи діагностику каналів E-Stop, кнопку
   мертвої руки та петлю EDM і керує котушками силових контакторів. */

#include <stdbool.h>
#include <stdint.h>

#include "deadman.h"
#include "estop_channels.h"

typedef enum {
    SAFETY_IDLE = 0,               /* безпечний стан після ввімкнення живлення */
    SAFETY_RUNNING,
    SAFETY_STOPPED_ESTOP,          /* натиснуто грибок або розірвано контур */
    SAFETY_STOPPED_ENABLE,         /* кнопка мертвої руки не в Позиції 2 */
    SAFETY_FAULT_SHORT_TO_SUPPLY,
    SAFETY_FAULT_CROSS_CIRCUIT,
    SAFETY_FAULT_DISCORDANCE,
    SAFETY_FAULT_ENABLE_CONTACTS,
    SAFETY_FAULT_EDM               /* контактор приварився або обірвано петлю */
} safety_state_t;

typedef struct {
    safety_state_t    state;
    estop_channels_t  channels;
    deadman_t         deadman;

    bool     contactors_on;
    bool     edm_watch;       /* чекаємо, поки дзеркальні контакти перекинуться */
    uint32_t edm_timer_ms;
    bool     reset_prev;
    uint32_t last_ms;
} safety_t;

/* Ініціалізація ставить контур у безпечний стан і знімає залиплі помилки:
   це дія обслуговування, а не автоматичне скидання. */
void safety_init(safety_t *s);

/* Викликати з головного циклу. Період — одиниці мілісекунд. */
void safety_process(safety_t *s);

bool           safety_is_fault(safety_state_t st);
const char    *safety_state_name(safety_state_t st);
safety_state_t safety_state(const safety_t *s);
bool           safety_outputs_on(const safety_t *s);

#endif /* SAFETY_H */

#ifndef EVSE_PATTERN_FSM_HANDLER_H
#define EVSE_PATTERN_FSM_HANDLER_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Патерн 3: покажчик на функцію стану. Поточний стан — це функція; вся логіка
 * одного стану, разом із діями входу й виходу, лежить в одному місці, а рушій
 * переходу вміщається в п'ять рядків.
 *
 * Приклад — керування насосною станцією: бак наповнюється, витримується й
 * спорожнюється, а сухий хід зупиняє насос негайно.
 */

typedef enum {
    PUMP_EV_ENTRY = 0, /* службовий: вхід у стан */
    PUMP_EV_EXIT,      /* службовий: вихід зі стану */
    PUMP_EV_LEVEL_HIGH,
    PUMP_EV_LEVEL_LOW,
    PUMP_EV_DRY_RUN,   /* давач тиску не бачить води на всмоктуванні */
    PUMP_EV_TIMER,
    PUMP_EV_RESET
} pump_signal_t;

typedef struct pump_s pump_t;
typedef void (*pump_state_fn)(pump_t *me, pump_signal_t sig);

struct pump_s {
    pump_state_fn state;
    uint32_t      cycles;      /* завершених циклів наповнення */
    uint16_t      hold_ticks;  /* лишилося тактів витримки */
    bool          dry_latched; /* сухий хід зафіксовано */
};

void pump_init(pump_t *me);
void pump_dispatch(pump_t *me, pump_signal_t sig);

const char *pump_state_name(const pump_t *me);

/*
 * Порт демонстрації. Слабкі означення в fsm_handler.c дозволяють зібрати
 * приклад без плати; на реальному пристрої їх перекриває драйвер GPIO.
 */
void pump_port_valve(bool open);
void pump_port_motor(bool run);
void pump_port_alarm(bool on);

#endif /* EVSE_PATTERN_FSM_HANDLER_H */

#ifndef EVSE_PATTERN_FSM_TABLE_H
#define EVSE_PATTERN_FSM_TABLE_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Патерн 2: декларативна матриця переходів. Граф живе не в коді, а в сталій
 * таблиці у Flash-пам'яті; диспетчер — вісім рядків, які не змінюються ніколи.
 * Приклад — охоронний шлейф із сиреною.
 */

typedef enum {
    SEC_ST_IDLE = 0,   /* знято з охорони */
    SEC_ST_ARMED,      /* під охороною */
    SEC_ST_ENTRY_DELAY,/* спрацював давач, іде час на введення коду */
    SEC_ST_TRIGGERED,  /* сирена */
    SEC_ST_COUNT
} sec_state_t;

typedef enum {
    SEC_SIG_PIR = 0,   /* інфрачервоний давач руху */
    SEC_SIG_CODE,      /* уведено правильний код */
    SEC_SIG_TIMEOUT,   /* сплив програмний таймер */
    SEC_SIG_COUNT
} sec_signal_t;

typedef struct sec_fsm_s sec_fsm_t;

struct sec_fsm_s {
    sec_state_t state;
    bool        siren_active;
    uint16_t    alarm_count;   /* скільки разів вили за зміну */
    uint32_t    timer_ms;      /* 0 — таймер знято */
};

void        sec_fsm_init(sec_fsm_t *fsm);
void        sec_fsm_dispatch(sec_fsm_t *fsm, sec_signal_t sig);

/* Плин часу: щойно заведений таймер доходить до нуля, автомат дістає
 * SEC_SIG_TIMEOUT — так само, як у справжній прошивці його дістав би з черги
 * подій обробник системного таймера. */
void        sec_fsm_tick(sec_fsm_t *fsm, uint32_t elapsed_ms);
const char *sec_state_name(sec_state_t s);

/*
 * Матриця відкрита назовні навмисно: за нею статичний аналізатор або
 * самоперевірка на старті проходять граф і доводять, що з кожного стану є
 * шлях назад у SEC_ST_IDLE.
 */
bool sec_fsm_graph_is_sane(void);

#endif /* EVSE_PATTERN_FSM_TABLE_H */

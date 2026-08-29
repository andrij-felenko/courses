/* attenuator.h — кроковий РЧ-атенюатор за SCPI через RS-232.
 * Керування асинхронне: постановка команди не блокує потік вибірок. */
#ifndef ATTENUATOR_H
#define ATTENUATOR_H

#include <stdbool.h>
#include <stddef.h>

#define ATT_MAX_DB   95.0
#define ATT_STEP_DB  0.25

typedef enum {
    ATT_IDLE,      /* автомат вільний */
    ATT_SENDING,   /* команда ще не дописана в порт */
    ATT_WAIT_ACK,  /* чекаємо відповідь на *OPC? */
    ATT_FAILED     /* прилад не відповідає — прогін далі не має сенсу */
} att_state_t;

typedef struct {
    int    fd;
    att_state_t state;

    char   tx[64];
    size_t tx_len, tx_sent;
    char   rx[128];
    size_t rx_len;

    double pending_db, current_db;
    int    retries;
    double deadline_ms;

    unsigned long commands, timeouts;
} attenuator_t;

bool attenuator_open(attenuator_t *a, const char *device);
void attenuator_close(attenuator_t *a);

/* Ставить нове загасання в роботу; false — автомат ще зайнятий або зламався. */
bool attenuator_request(attenuator_t *a, double db);

/* Рухає автомат уперед. Викликається щокроку циклу й ніколи не блокує. */
void attenuator_poll(attenuator_t *a);

static inline bool attenuator_busy(const attenuator_t *a) { return a->state != ATT_IDLE; }

#endif /* ATTENUATOR_H */

#ifndef CONN_FSM_H
#define CONN_FSM_H

#include "mqtt_min.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Стани життєвого циклу з'єднання. Порядок значущий: обробники URC
   порівнюють стани між собою («ми вже глибше за реєстрацію?»). */
typedef enum {
    CONN_NO_POWER = 0,
    CONN_POWERING_ON,
    CONN_MODEM_READY,
    CONN_SIM_READY,
    CONN_NET_SEARCH,
    CONN_IP_ATTACH,
    CONN_TCP_CONNECT,
    CONN_PROTOCOL_AUTH,
    CONN_READY_TO_SEND,
    CONN_SENDING,
    CONN_DISCONNECTING,
    CONN_PSM_SLEEP,
    CONN_BACKOFF,
    CONN_HW_RESET,
    CONN_POWER_CYCLE,
    CONN_FATAL_STOP
} conn_state_t;

#define CONN_TX_MAX 256u

typedef struct {
    conn_state_t state;
    conn_state_t backoff_target;

    uint32_t enter_ms;
    uint32_t timeout_ms;       /* 0 — стан без таймауту */
    uint32_t poll_period_ms;   /* періодичне опитування, 0 — вимкнено */
    uint32_t poll_last_ms;

    uint8_t  substep;          /* крок усередині стану */
    uint8_t  probes;           /* спроби синхронізації "AT" */
    uint8_t  level;            /* поточна сходинка драбини відновлення */
    uint8_t  retry;            /* спроб на цій сходинці */

    uint8_t  last_event;       /* для чорної скриньки */
    uint16_t last_cme;
    int8_t   rssi_dbm;

    bool     ping_pending;     /* чекаємо на PINGRESP */
    bool     want_disconnect;
    bool     log_pending;      /* чорна скринька чекає на відправку */
    bool     tx_pending;
    bool     tx_is_log;
    uint16_t packet_id;

    uint8_t  tx[CONN_TX_MAX];  /* корисне навантаження в черзі */
    size_t   tx_len;
    uint8_t  out[CONN_TX_MAX + 64u]; /* кадр MQTT, що чекає на '>' */
    size_t   out_len;

    mqtt_rx_t mqtt;
} conn_fsm_t;

void conn_fsm_init(conn_fsm_t *f);

/* Квант диспетчеризації: викликати з суперциклу кожні 10–50 мс. */
void conn_fsm_tick(conn_fsm_t *f);

void conn_fsm_connect(conn_fsm_t *f);
bool conn_fsm_submit(conn_fsm_t *f, const uint8_t *payload, size_t len);
void conn_fsm_disconnect(conn_fsm_t *f);

conn_state_t conn_fsm_state(const conn_fsm_t *f);
bool conn_fsm_idle(const conn_fsm_t *f); /* сесія жива, черга порожня */

#endif /* CONN_FSM_H */

/* Бортовий вузол: скінченний автомат селектора з розділу 3 профілю. */
#ifndef SBO_NODE_H
#define SBO_NODE_H

#include "sbo_proto.h"

/* Стан приводів, який чіпають критичні команди. Тут він удаваний —
   у прошивці на його місці регістри ESC, реле та прапорці автопілота. */
struct sbo_actuators {
    bool    motors_live;
    bool    armed;
    bool    reboot_pending;
    bool    params_default;
    bool    payload_dropped;   /* одноразовий замок скидача */
    uint8_t flight_mode;
    bool    healthy;           /* кінцевик/перегрів: чи готова підсистема */
};

struct sbo_node {
    uint8_t  node_id;
    uint8_t  seq;              /* лічильник власних відповідей */
    uint8_t  state;
    uint8_t  flags;            /* SBO_FLAG_* для пакета стану */
    uint32_t rng;

    /* Замок селекції — дійсний лише в стані ARMED. */
    uint8_t  owner;            /* source_id пульта, що взяв замок */
    uint8_t  comp;
    uint16_t cmd_code;
    uint32_t token;
    uint32_t deadline_ms;

    uint32_t expired_token;    /* останній токен, що згорів за таймером */
    uint32_t cooldown_until_ms;

    uint32_t security_drops;   /* журнал безпеки: тихо відкинуті кадри */
    uint32_t rx_errors;        /* биті кадри: magic, довжина, CRC */
    uint32_t rejects;

    uint8_t  password[4];      /* пароль для CMD_FACTORY_RESET_PARAMS */
    struct sbo_actuators act;
};

void sbo_node_init(struct sbo_node *n, uint8_t node_id, uint32_t seed);

/* Старіння замка: викликається з періодичної задачі й перед розбором кадру. */
void sbo_node_tick(struct sbo_node *n, uint32_t now_ms);

/* Обробляє прийнятий кадр. Повертає довжину відповіді або 0, якщо
   відповідати нікому й не треба (кадр битий, чужий або відкинутий фільтром). */
size_t sbo_node_handle(struct sbo_node *n, const uint8_t *in, size_t in_len,
                       uint32_t now_ms, uint8_t *out, size_t out_cap);

uint16_t sbo_node_remaining_ms(const struct sbo_node *n, uint32_t now_ms);
uint8_t  sbo_node_heartbeat_flags(const struct sbo_node *n);

#endif /* SBO_NODE_H */

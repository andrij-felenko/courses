/* Фільтрація кадру в обробнику вхідних пакетів мовою C */
#include <stdint.h>
#include <stdbool.h>

#define SBO_BROADCAST_ID        0xFF
#define CMD_CRITICAL_THRESHOLD  0x0100

typedef struct {
    uint8_t  target_id;
    uint16_t cmd_code;
    uint32_t sbo_token;
} sbo_rx_frame_t;

typedef struct {
    uint8_t  state;       /* 0: IDLE, 1: ARMED */
    uint32_t active_token;
} sbo_gate_state_t;

bool security_gate_validate_packet(const sbo_rx_frame_t *pkt, 
                                   uint8_t my_id, 
                                   const sbo_gate_state_t *gate) {
    /* Ступінь 1: Перевірка адреси */
    if (pkt->target_id == SBO_BROADCAST_ID) {
        /* Широкомовні пакети дозволені ТІЛЬКИ для службового моніторингу */
        if (pkt->cmd_code >= CMD_CRITICAL_THRESHOLD) {
            return false; /* Заборона критичної дії на 0xFF */
        }
    } else if (pkt->target_id != my_id) {
        return false; /* Чужий пакет, негайне відкидання без обробки */
    }

    /* Ступінь 2: Перевірка транзакційного стану SBO */
    if (pkt->cmd_code >= CMD_CRITICAL_THRESHOLD) {
        if (gate->state != 1) {
            return false; /* Спроба прямої дії без попереднього вибору */
        }
        if (pkt->sbo_token != gate->active_token) {
            return false; /* Недійсний або підроблений токен блокування */
        }
    }

    return true; /* Пакет авторизовано */
}

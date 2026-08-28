// att_engine.h / att_engine.c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define ATT_DEFAULT_MTU         23
#define ATT_MAX_MTU             517
#define ATT_TRANSACTION_TIMEOUT 30000 // 30 секунд у мілісекундах

// Коди операцій протоколу ATT
typedef enum {
    ATT_OP_ERROR_RSP            = 0x01,
    ATT_OP_EXCHANGE_MTU_REQ     = 0x02,
    ATT_OP_EXCHANGE_MTU_RSP     = 0x03,
    ATT_OP_READ_BY_TYPE_REQ     = 0x08,
    ATT_OP_READ_BY_TYPE_RSP     = 0x09,
    ATT_OP_READ_REQ             = 0x0A,
    ATT_OP_READ_RSP             = 0x0B,
    ATT_OP_WRITE_REQ            = 0x12,
    ATT_OP_WRITE_RSP            = 0x13,
    ATT_OP_WRITE_CMD            = 0x52,
    ATT_OP_HANDLE_VALUE_NTF     = 0x1B,
    ATT_OP_HANDLE_VALUE_IND     = 0x1D,
    ATT_OP_HANDLE_VALUE_CFM     = 0x1E
} att_opcode_t;

// Стани клієнтського автомата транзакцій
typedef enum {
    ATT_STATE_IDLE,
    ATT_STATE_WAITING_RESPONSE,
    ATT_STATE_TIMED_OUT
} att_fsm_state_t;

// Розібраний пакет ATT без дублювання даних
typedef struct {
    att_opcode_t opcode;
    uint16_t     handle;
    uint16_t     offset;
    uint8_t      error_code;
    uint8_t      req_opcode_in_err;
    const uint8_t* value_data;
    size_t       value_len;
} att_packet_t;

// Стан клієнтського контексту ATT
typedef struct {
    att_fsm_state_t state;
    att_opcode_t    pending_req_opcode;
    uint16_t        pending_req_handle;
    uint32_t        timer_start_ms;
    uint16_t        effective_mtu;
} att_client_t;

// Безпечне витягнення 16-бітного числа у форматі Little-Endian
static inline uint16_t att_read_le16(const uint8_t* ptr) {
    return (uint16_t)ptr[0] | ((uint16_t)ptr[1] << 8);
}

// Запис 16-бітного числа у форматі Little-Endian
static inline void att_write_le16(uint8_t* ptr, uint16_t val) {
    ptr[0] = (uint8_t)(val & 0xFF);
    ptr[1] = (uint8_t)((val >> 8) & 0xFF);
}

// Ініціалізація клієнтського контексту
void att_client_init(att_client_t* client) {
    client->state = ATT_STATE_IDLE;
    client->pending_req_opcode = 0;
    client->pending_req_handle = 0;
    client->timer_start_ms = 0;
    client->effective_mtu = ATT_DEFAULT_MTU;
}

// Безпечний парсер вхідного кадру L2CAP
bool att_parse_packet(const uint8_t* buf, size_t len, att_packet_t* pkt) {
    if (!buf || len == 0 || !pkt) return false;
    memset(pkt, 0, sizeof(att_packet_t));
    pkt->opcode = (att_opcode_t)buf[0];

    switch (pkt->opcode) {
        case ATT_OP_ERROR_RSP:
            if (len != 5) return false;
            pkt->req_opcode_in_err = buf[1];
            pkt->handle            = att_read_le16(&buf[2]);
            pkt->error_code        = buf[4];
            return true;

        case ATT_OP_EXCHANGE_MTU_REQ:
        case ATT_OP_EXCHANGE_MTU_RSP:
            if (len != 3) return false;
            pkt->handle = att_read_le16(&buf[1]); // поле MTU
            return (pkt->handle >= ATT_DEFAULT_MTU);

        case ATT_OP_READ_REQ:
            if (len != 3) return false;
            pkt->handle = att_read_le16(&buf[1]);
            return (pkt->handle != 0x0000);

        case ATT_OP_READ_RSP:
            pkt->value_data = (len > 1) ? &buf[1] : NULL;
            pkt->value_len  = (len > 1) ? (len - 1) : 0;
            return true;

        case ATT_OP_WRITE_REQ:
        case ATT_OP_WRITE_CMD:
        case ATT_OP_HANDLE_VALUE_NTF:
        case ATT_OP_HANDLE_VALUE_IND:
            if (len < 3) return false;
            pkt->handle     = att_read_le16(&buf[1]);
            pkt->value_data = (len > 3) ? &buf[3] : NULL;
            pkt->value_len  = (len > 3) ? (len - 3) : 0;
            return (pkt->handle != 0x0000);

        case ATT_OP_WRITE_RSP:
        case ATT_OP_HANDLE_VALUE_CFM:
            return (len == 1);

        default:
            return false;
    }
}

// Спроба відправки запиту клієнтом
bool att_client_send_request(att_client_t* client, att_opcode_t req_op,
                            uint16_t handle, uint32_t now_ms) {
    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        return false; // Канал заблоковано активною транзакцією!
    }
    client->pending_req_opcode = req_op;
    client->pending_req_handle = handle;
    client->timer_start_ms     = now_ms;
    client->state              = ATT_STATE_WAITING_RESPONSE;
    return true;
}

// Обробка прийому пакета від сервера
bool att_client_on_rx(att_client_t* client, const uint8_t* buf,
                      size_t len, att_packet_t* out_pkt) {
    if (!att_parse_packet(buf, len, out_pkt)) {
        return false;
    }

    // Асинхронні сповіщення не розблоковують чергу запитів
    if (out_pkt->opcode == ATT_OP_HANDLE_VALUE_NTF) {
        return true;
    }

    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        bool matches = false;

        if (out_pkt->opcode == ATT_OP_ERROR_RSP) {
            matches = (out_pkt->req_opcode_in_err == client->pending_req_opcode);
        } else if (client->pending_req_opcode == ATT_OP_READ_REQ &&
                   out_pkt->opcode == ATT_OP_READ_RSP) {
            matches = true;
        } else if (client->pending_req_opcode == ATT_OP_WRITE_REQ &&
                   out_pkt->opcode == ATT_OP_WRITE_RSP) {
            matches = true;
        } else if (client->pending_req_opcode == ATT_OP_EXCHANGE_MTU_REQ &&
                   out_pkt->opcode == ATT_OP_EXCHANGE_MTU_RSP) {
            client->effective_mtu = (out_pkt->handle < ATT_MAX_MTU) ?
                                     out_pkt->handle : ATT_MAX_MTU;
            matches = true;
        }

        if (matches) {
            client->state = ATT_STATE_IDLE;
            client->pending_req_opcode = 0;
            client->pending_req_handle = 0;
            return true;
        }
    }
    return true;
}

// Перевірка спрацювання таймауту 30 секунд
bool att_client_poll_timeout(att_client_t* client, uint32_t now_ms) {
    if (client->state == ATT_STATE_WAITING_RESPONSE) {
        if ((now_ms - client->timer_start_ms) >= ATT_TRANSACTION_TIMEOUT) {
            client->state = ATT_STATE_TIMED_OUT;
            return true; // Спрацював обов'язковий розрив зв'язку!
        }
    }
    return false;
}

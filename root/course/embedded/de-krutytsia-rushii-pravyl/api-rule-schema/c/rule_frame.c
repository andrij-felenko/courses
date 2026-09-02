#include "rule_frame.h"

#include <string.h>

/* Тіньовий буфер прийому. Об'єднання дає і байтовий доступ, і вирівняне
   накладання масиву дескрипторів — без копіювання поле за полем. */
typedef union {
    uint8_t           bytes[MAX_RULES_COUNT * RULE_DESCRIPTOR_SIZE];
    rule_descriptor_t rules[MAX_RULES_COUNT];
} rule_payload_view_t;

static rule_payload_view_t g_shadow;

uint16_t rule_frame_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFu;                     /* CRC-16-CCITT, поліном 0x1021 */
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int b = 0; b < 8; ++b) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

size_t rule_frame_encode(uint8_t type, const uint8_t *payload, uint16_t payload_len,
                         uint8_t *out, size_t out_cap) {
    size_t total = FRAME_HEADER_SIZE + payload_len + FRAME_CRC_SIZE;
    if (out_cap < total) { return 0; }

    out[0] = FRAME_SOF_HI;
    out[1] = FRAME_SOF_LO;
    out[2] = (uint8_t)(payload_len & 0xFFu);        /* Length, Little-Endian */
    out[3] = (uint8_t)(payload_len >> 8);
    out[4] = type;
    if (payload_len > 0) { memcpy(&out[FRAME_HEADER_SIZE], payload, payload_len); }

    /* CRC рахується по Length, Type і Payload — синхробайти в суму не входять. */
    uint16_t crc = rule_frame_crc16(&out[2], (size_t)payload_len + 3u);
    out[FRAME_HEADER_SIZE + payload_len]      = (uint8_t)(crc & 0xFFu);
    out[FRAME_HEADER_SIZE + payload_len + 1u] = (uint8_t)(crc >> 8);
    return total;
}

size_t rule_frame_encode_table(const rule_descriptor_t *table, uint8_t count,
                               uint8_t *out, size_t out_cap) {
    if (count > MAX_RULES_COUNT) { return 0; }
    uint16_t payload_len = (uint16_t)(count * RULE_DESCRIPTOR_SIZE);
    return rule_frame_encode(FRAME_TYPE_RULE_TABLE,
                             (const uint8_t *)table, payload_len, out, out_cap);
}

static size_t build_reply(uint8_t type, uint8_t code, uint8_t *reply, size_t cap) {
    return rule_frame_encode(type, &code, 1u, reply, cap);
}

rule_error_t rule_frame_handle(rule_engine_t *e, const uint8_t *frame, size_t len,
                               uint8_t *reply, size_t reply_cap, size_t *reply_len) {
    rule_error_t err = ERR_NONE;
    uint8_t ack_payload = 0;

    if (len < FRAME_MIN_SIZE || len > FRAME_MAX_SIZE) {
        err = ERR_TRUNCATED_FRAME;
        goto answer;
    }
    if (frame[0] != FRAME_SOF_HI || frame[1] != FRAME_SOF_LO) {
        err = ERR_BAD_SOF;
        goto answer;
    }

    uint16_t payload_len = (uint16_t)(frame[2] | ((uint16_t)frame[3] << 8));
    if ((size_t)payload_len + FRAME_HEADER_SIZE + FRAME_CRC_SIZE != len) {
        err = ERR_TRUNCATED_FRAME;
        goto answer;
    }

    /* 1. Цілісність. Побитий кадр не має шансу дійти до розбору полів. */
    uint16_t got  = (uint16_t)(frame[FRAME_HEADER_SIZE + payload_len] |
                    ((uint16_t)frame[FRAME_HEADER_SIZE + payload_len + 1u] << 8));
    uint16_t want = rule_frame_crc16(&frame[2], (size_t)payload_len + 3u);
    if (got != want) {
        err = ERR_CRC_MISMATCH;
        goto answer;
    }

    if (frame[4] != FRAME_TYPE_RULE_TABLE) {
        err = ERR_UNKNOWN_TYPE;
        goto answer;
    }
    if ((payload_len % RULE_DESCRIPTOR_SIZE) != 0) {
        err = ERR_LENGTH_ALIGN;
        goto answer;
    }

    /* 2. Ліміт пам'яті: у тіньовий буфер більше за MAX_RULES_COUNT не влізе. */
    uint16_t count = (uint16_t)(payload_len / RULE_DESCRIPTOR_SIZE);
    if (count > MAX_RULES_COUNT) {
        err = ERR_BUFFER_OVERFLOW;
        goto answer;
    }

    memcpy(g_shadow.bytes, &frame[FRAME_HEADER_SIZE], payload_len);

    /* 3. Семантика: опкоди, індекси регістрів, недоторканність захисту. */
    err = rule_engine_validate_table(e, g_shadow.rules, (uint8_t)count);
    if (err != ERR_NONE) { goto answer; }

    /* 4. Атомарне перемикання під забороненими перериваннями. */
    rule_engine_commit_table(e, g_shadow.rules, (uint8_t)count);
    ack_payload = (uint8_t)count;

answer:
    if (reply != NULL && reply_len != NULL) {
        *reply_len = (err == ERR_NONE)
            ? build_reply(FRAME_TYPE_ACK, ack_payload, reply, reply_cap)
            : build_reply(FRAME_TYPE_NACK, (uint8_t)err, reply, reply_cap);
    }
    return err;
}

const char *rule_error_str(rule_error_t err) {
    switch (err) {
        case ERR_NONE:             return "OK";
        case ERR_BAD_SOF:          return "ERR_BAD_SOF";
        case ERR_TRUNCATED_FRAME:  return "ERR_TRUNCATED_FRAME";
        case ERR_UNKNOWN_TYPE:     return "ERR_UNKNOWN_TYPE";
        case ERR_LENGTH_ALIGN:     return "ERR_LENGTH_ALIGN";
        case ERR_CRC_MISMATCH:     return "ERR_CRC_MISMATCH";
        case ERR_BUFFER_OVERFLOW:  return "ERR_BUFFER_OVERFLOW";
        case ERR_BAD_OPCODE:       return "ERR_BAD_OPCODE";
        case ERR_REG_OUT_OF_RANGE: return "ERR_REG_OUT_OF_RANGE";
        case ERR_BAD_RESERVED:     return "ERR_BAD_RESERVED";
        case ERR_BAD_FLAGS:        return "ERR_BAD_FLAGS";
        case ERR_BAD_RULE_ID:      return "ERR_BAD_RULE_ID";
        case ERR_DUPLICATE_ID:     return "ERR_DUPLICATE_ID";
        case ERR_SAFETY_VIOLATION: return "ERR_SAFETY_VIOLATION";
        case ERR_REG_READ_ONLY:    return "ERR_REG_READ_ONLY";
        case ERR_REMOTE_INHIBITED: return "ERR_REMOTE_INHIBITED";
        default:                   return "ERR_UNKNOWN";
    }
}

/* sbo_protocol.c — кодування, декодування й перевірка кадру SBO. */
#include "sbo_protocol.h"

#include <string.h>

static void put_u16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static uint16_t get_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

uint16_t sbo_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8u; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

bool sbo_msg_type_is_known(uint8_t msg_type) {
    switch (msg_type) {
    case SBO_MSG_SELECT_REQ:
    case SBO_MSG_SELECT_ACK:
    case SBO_MSG_SELECT_NACK:
    case SBO_MSG_OPERATE_REQ:
    case SBO_MSG_OPERATE_ACK:
    case SBO_MSG_OPERATE_NACK:
    case SBO_MSG_CANCEL_REQ:
    case SBO_MSG_CANCEL_ACK:
    case SBO_MSG_CANCEL_NACK:
        return true;
    default:
        return false;
    }
}

sbo_error_t sbo_frame_encode(const sbo_packet_t *pkt, uint8_t *buf, size_t cap, size_t *out_len) {
    if (pkt == NULL || buf == NULL || out_len == NULL) {
        return SBO_ERR_INTERNAL_FAULT;
    }
    if (pkt->payload_len > SBO_MAX_PAYLOAD_LEN) {
        return SBO_ERR_BAD_LENGTH;
    }

    const size_t body_len  = (size_t)SBO_HEADER_LEN + pkt->payload_len;
    const size_t frame_len = body_len + SBO_CRC_LEN;
    if (cap < frame_len) {
        return SBO_ERR_BAD_LENGTH;
    }

    buf[0] = SBO_MAGIC_BYTE;
    buf[1] = pkt->payload_len;
    buf[2] = pkt->seq;
    buf[3] = pkt->msg_type;
    buf[4] = pkt->source_id;
    buf[5] = pkt->target_id;
    buf[6] = pkt->target_comp;
    buf[7] = pkt->sbo_state;
    put_u32(&buf[8], pkt->sbo_token);
    put_u16(&buf[12], pkt->cmd_code);
    put_u16(&buf[14], pkt->timeout_ms);
    memcpy(&buf[SBO_HEADER_LEN], pkt->payload, pkt->payload_len);
    put_u16(&buf[body_len], sbo_crc16(buf, body_len));

    *out_len = frame_len;
    return SBO_ERR_NONE;
}

sbo_error_t sbo_frame_decode(const uint8_t *buf, size_t len, sbo_packet_t *out) {
    if (buf == NULL || out == NULL) {
        return SBO_ERR_INTERNAL_FAULT;
    }
    if (len < SBO_MIN_FRAME_LEN || len > SBO_MAX_FRAME_LEN) {
        return SBO_ERR_BAD_LENGTH;
    }
    if (buf[0] != SBO_MAGIC_BYTE) {
        return SBO_ERR_BAD_MAGIC;
    }

    const uint8_t payload_len = buf[1];
    if (payload_len > SBO_MAX_PAYLOAD_LEN) {
        return SBO_ERR_BAD_LENGTH;
    }
    const size_t body_len = (size_t)SBO_HEADER_LEN + payload_len;
    if (len != body_len + SBO_CRC_LEN) {
        return SBO_ERR_BAD_LENGTH;   /* заявлена довжина не збігається з отриманою */
    }
    if (get_u16(&buf[body_len]) != sbo_crc16(buf, body_len)) {
        return SBO_ERR_BAD_CRC;
    }
    if (!sbo_msg_type_is_known(buf[3])) {
        return SBO_ERR_UNKNOWN_TYPE;
    }

    memset(out, 0, sizeof(*out));
    out->magic       = buf[0];
    out->payload_len = payload_len;
    out->seq         = buf[2];
    out->msg_type    = buf[3];
    out->source_id   = buf[4];
    out->target_id   = buf[5];
    out->target_comp = buf[6];
    out->sbo_state   = buf[7];
    out->sbo_token   = get_u32(&buf[8]);
    out->cmd_code    = get_u16(&buf[12]);
    out->timeout_ms  = get_u16(&buf[14]);
    memcpy(out->payload, &buf[SBO_HEADER_LEN], payload_len);
    return SBO_ERR_NONE;
}

const char *sbo_error_text(sbo_error_t err) {
    switch (err) {
    case SBO_ERR_NONE:                return "ok";
    case SBO_ERR_BUSY:                return "зайнято іншим оператором";
    case SBO_ERR_INVALID_TOKEN:       return "недійсний токен";
    case SBO_ERR_TIMEOUT_EXPIRED:     return "вікно селекції спливло";
    case SBO_ERR_NOT_ARMED:           return "замок не зведено";
    case SBO_ERR_CMD_MISMATCH:        return "команда не та, що вибиралася";
    case SBO_ERR_SOURCE_MISMATCH:     return "токен з чужої адреси";
    case SBO_ERR_BROADCAST_FORBIDDEN: return "широкомовна критична дія заборонена";
    case SBO_ERR_FOREIGN_TARGET:      return "кадр адресовано іншому вузлу";
    case SBO_ERR_BAD_MAGIC:           return "чужий кадр (magic)";
    case SBO_ERR_BAD_LENGTH:          return "неправильна довжина кадру";
    case SBO_ERR_BAD_CRC:             return "CRC не збігся";
    case SBO_ERR_UNKNOWN_TYPE:        return "невідомий тип повідомлення";
    default:                          return "внутрішня помилка";
    }
}

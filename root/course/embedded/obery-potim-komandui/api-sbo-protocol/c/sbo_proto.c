/* Кодек кадру SBO: контрольна сума, збирання та розбір. */
#include "sbo_proto.h"

#include <string.h>

uint16_t sbo_crc16_ccitt(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000u) {
                crc = (uint16_t)((crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

/* Багатобайтові поля — Little-Endian, як вимагає розділ 1. */
static void put_u16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

static void put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8) & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static uint16_t get_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t get_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

size_t sbo_encode(const struct sbo_frame *f, uint8_t *out, size_t cap)
{
    if (f->payload_len > SBO_MAX_PAYLOAD) {
        return 0;
    }
    const size_t body = SBO_HEADER_LEN + f->payload_len;
    const size_t total = body + SBO_CRC_LEN;
    if (cap < total) {
        return 0;
    }

    out[0] = SBO_MAGIC;
    out[1] = f->payload_len;
    out[2] = f->seq;
    out[3] = f->msg_type;
    out[4] = f->source_id;
    out[5] = f->target_id;
    out[6] = f->target_comp;
    out[7] = f->sbo_state;
    put_u32(out + 8, f->sbo_token);
    put_u16(out + 12, f->cmd_code);
    put_u16(out + 14, f->timeout_ms);
    memcpy(out + SBO_HEADER_LEN, f->payload, f->payload_len);

    /* Сума охоплює все від magic до кінця payload. */
    put_u16(out + body, sbo_crc16_ccitt(out, body));
    return total;
}

enum sbo_decode_result sbo_decode(const uint8_t *buf, size_t len, struct sbo_frame *out)
{
    if (len < SBO_HEADER_LEN + SBO_CRC_LEN) {
        return SBO_DECODE_SHORT;
    }
    if (buf[0] != SBO_MAGIC) {
        return SBO_DECODE_BAD_MAGIC;
    }

    const uint8_t n = buf[1];
    if (n > SBO_MAX_PAYLOAD) {
        return SBO_DECODE_BAD_LEN;
    }

    const size_t body = SBO_HEADER_LEN + (size_t)n;
    const size_t total = body + SBO_CRC_LEN;
    if (len < total) {
        return SBO_DECODE_SHORT;
    }
    if (len > total) {
        /* Хвіст після контрольної суми — злиплі кадри або сміття в ефірі. */
        return SBO_DECODE_BAD_LEN;
    }
    if (get_u16(buf + body) != sbo_crc16_ccitt(buf, body)) {
        return SBO_DECODE_BAD_CRC;
    }

    memset(out, 0, sizeof(*out));
    out->payload_len = n;
    out->seq         = buf[2];
    out->msg_type    = buf[3];
    out->source_id   = buf[4];
    out->target_id   = buf[5];
    out->target_comp = buf[6];
    out->sbo_state   = buf[7];
    out->sbo_token   = get_u32(buf + 8);
    out->cmd_code    = get_u16(buf + 12);
    out->timeout_ms  = get_u16(buf + 14);
    memcpy(out->payload, buf + SBO_HEADER_LEN, n);
    return SBO_DECODE_OK;
}

bool sbo_cmd_is_critical(uint16_t cmd_code)
{
    return cmd_code >= SBO_CRITICAL_BASE;
}

uint16_t sbo_clamp_window(uint16_t timeout_ms)
{
    if (timeout_ms == 0) {
        return (uint16_t)SBO_T_ARM_DEFAULT_MS;   /* пульт не назвав вікна */
    }
    if (timeout_ms < SBO_T_ARM_MIN_MS) {
        return (uint16_t)SBO_T_ARM_MIN_MS;
    }
    if (timeout_ms > SBO_T_ARM_MAX_MS) {
        return (uint16_t)SBO_T_ARM_MAX_MS;
    }
    return timeout_ms;
}

const char *sbo_msg_name(uint8_t msg_type)
{
    switch (msg_type) {
    case SBO_MSG_SELECT_REQ:   return "SELECT_REQ";
    case SBO_MSG_SELECT_ACK:   return "SELECT_ACK";
    case SBO_MSG_SELECT_NACK:  return "SELECT_NACK";
    case SBO_MSG_OPERATE_REQ:  return "OPERATE_REQ";
    case SBO_MSG_OPERATE_ACK:  return "OPERATE_ACK";
    case SBO_MSG_OPERATE_NACK: return "OPERATE_NACK";
    case SBO_MSG_CANCEL_REQ:   return "CANCEL_REQ";
    case SBO_MSG_CANCEL_ACK:   return "CANCEL_ACK";
    case SBO_MSG_STATUS_PING:  return "STATUS_PING";
    case SBO_MSG_STATUS_PONG:  return "STATUS_PONG";
    default:                   return "UNKNOWN";
    }
}

const char *sbo_state_name(uint8_t state)
{
    switch (state) {
    case SBO_STATE_IDLE:      return "IDLE";
    case SBO_STATE_ARMED:     return "ARMED";
    case SBO_STATE_EXECUTING: return "EXECUTING";
    default:                  return "?";
    }
}

const char *sbo_error_name(uint8_t code)
{
    switch (code) {
    case ERR_SBO_BUSY:                return "ERR_SBO_BUSY";
    case ERR_SBO_INVALID_TOKEN:       return "ERR_SBO_INVALID_TOKEN";
    case ERR_SBO_TIMEOUT_EXPIRED:     return "ERR_SBO_TIMEOUT_EXPIRED";
    case ERR_SBO_NOT_ARMED:           return "ERR_SBO_NOT_ARMED";
    case ERR_SBO_CMD_MISMATCH:        return "ERR_SBO_CMD_MISMATCH";
    case ERR_SBO_BROADCAST_FORBIDDEN: return "ERR_SBO_BROADCAST_FORBIDDEN";
    case ERR_SBO_HARDWARE_FAULT:      return "ERR_SBO_HARDWARE_FAULT";
    default:                          return "ERR_UNKNOWN";
    }
}

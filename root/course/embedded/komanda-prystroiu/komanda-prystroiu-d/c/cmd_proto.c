#include "cmd_proto.h"

#include <string.h>

/* Зсуви полів кадру команди */
#define OFF_MAGIC 0u
#define OFF_VER   4u
#define OFF_TYPE  5u
#define OFF_SEQ   6u
#define OFF_TOKEN 10u
#define OFF_TTL   18u
#define OFF_PLEN  22u

/* Зсуви полів кадру квитанції */
#define AOFF_MAGIC  0u
#define AOFF_VER    4u
#define AOFF_PHASE  5u
#define AOFF_STATE  6u
#define AOFF_TOKEN  7u
#define AOFF_RESULT 15u
#define AOFF_DETAIL 19u
#define AOFF_CRC    23u

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v      );
    p[1] = (uint8_t)(v >>  8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void put_u64(uint8_t *p, uint64_t v) {
    put_u32(p,     (uint32_t)(v & 0xFFFFFFFFu));
    put_u32(p + 4, (uint32_t)(v >> 32));
}

static uint64_t get_u64(const uint8_t *p) {
    return (uint64_t)get_u32(p) | ((uint64_t)get_u32(p + 4) << 32);
}

void wire_put_u16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v);
    p[1] = (uint8_t)(v >> 8);
}

uint16_t wire_get_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

void wire_put_i32(uint8_t *p, int32_t v) {
    put_u32(p, (uint32_t)v);
}

int32_t wire_get_i32(const uint8_t *p) {
    return (int32_t)get_u32(p);
}

/* CRC-32 (поліном 0xEDB88320, відображений) без таблиці: на МК зайві 1 КБ
 * флешу під таблицю часто дорожчі за кілька мікросекунд обчислення. */
uint32_t wire_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            uint32_t mask = (uint32_t)0 - (crc & 1u);
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

cmd_err_t wire_parse_command(const uint8_t *buf, size_t len, cmd_frame_t *out) {
    if (buf == NULL || out == NULL) return E_BAD_LENGTH;
    if (len < CMD_HDR_LEN + 4u)     return E_SHORT_FRAME;

    if (get_u32(buf + OFF_MAGIC) != WIRE_MAGIC_CMD) return E_BAD_MAGIC;
    if (buf[OFF_VER] != WIRE_VERSION)               return E_BAD_VERSION;

    uint8_t plen = buf[OFF_PLEN];
    if (plen > CMD_MAX_PAYLOAD) return E_BAD_LENGTH;

    size_t total = (size_t)CMD_HDR_LEN + plen + 4u;
    if (len < total) return E_SHORT_FRAME;

    uint32_t crc_rx = get_u32(buf + total - 4u);
    if (wire_crc32(buf, total - 4u) != crc_rx) return E_BAD_CRC;

    memset(out, 0, sizeof(*out));
    out->type        = buf[OFF_TYPE];
    out->seq         = get_u32(buf + OFF_SEQ);
    out->token       = get_u64(buf + OFF_TOKEN);
    out->ttl_ms      = get_u32(buf + OFF_TTL);
    out->payload_len = plen;
    if (plen > 0) memcpy(out->payload, buf + CMD_HDR_LEN, plen);

    return E_OK;
}

size_t wire_build_command(const cmd_frame_t *f, uint8_t *buf, size_t cap) {
    if (f->payload_len > CMD_MAX_PAYLOAD) return 0;
    size_t total = (size_t)CMD_HDR_LEN + f->payload_len + 4u;
    if (cap < total) return 0;

    put_u32(buf + OFF_MAGIC, WIRE_MAGIC_CMD);
    buf[OFF_VER]  = WIRE_VERSION;
    buf[OFF_TYPE] = f->type;
    put_u32(buf + OFF_SEQ,   f->seq);
    put_u64(buf + OFF_TOKEN, f->token);
    put_u32(buf + OFF_TTL,   f->ttl_ms);
    buf[OFF_PLEN] = f->payload_len;
    if (f->payload_len > 0) memcpy(buf + CMD_HDR_LEN, f->payload, f->payload_len);

    put_u32(buf + total - 4u, wire_crc32(buf, total - 4u));
    return total;
}

size_t wire_build_ack(const ack_t *a, uint8_t *buf, size_t cap) {
    if (cap < ACK_FRAME_LEN) return 0;

    put_u32(buf + AOFF_MAGIC, WIRE_MAGIC_ACK);
    buf[AOFF_VER]   = WIRE_VERSION;
    buf[AOFF_PHASE] = a->phase;
    buf[AOFF_STATE] = a->state;
    put_u64(buf + AOFF_TOKEN,  a->token);
    put_u32(buf + AOFF_RESULT, (uint32_t)a->result);
    put_u32(buf + AOFF_DETAIL, (uint32_t)a->detail);
    put_u32(buf + AOFF_CRC,    wire_crc32(buf, AOFF_CRC));
    return ACK_FRAME_LEN;
}

bool wire_parse_ack(const uint8_t *buf, size_t len, ack_t *out) {
    if (len < ACK_FRAME_LEN)                        return false;
    if (get_u32(buf + AOFF_MAGIC) != WIRE_MAGIC_ACK) return false;
    if (buf[AOFF_VER] != WIRE_VERSION)               return false;
    if (wire_crc32(buf, AOFF_CRC) != get_u32(buf + AOFF_CRC)) return false;

    out->token  = get_u64(buf + AOFF_TOKEN);
    out->phase  = buf[AOFF_PHASE];
    out->state  = buf[AOFF_STATE];
    out->result = (int32_t)get_u32(buf + AOFF_RESULT);
    out->detail = (int32_t)get_u32(buf + AOFF_DETAIL);
    return true;
}

const char *cmd_type_name(uint8_t type) {
    switch (type) {
        case CMD_NOOP:        return "NOOP";
        case CMD_SET_RELAY:   return "SET_RELAY";
        case CMD_GOTO_POS:    return "GOTO_POS";
        case CMD_DISPENSE_ML: return "DISPENSE_ML";
        case CMD_CALIBRATE:   return "CALIBRATE";
        default:              return "?";
    }
}

const char *cmd_state_name(uint8_t state) {
    switch (state) {
        case ST_FREE:      return "FREE";
        case ST_ACCEPTED:  return "ACCEPTED";
        case ST_EXECUTING: return "EXECUTING";
        case ST_SUCCEEDED: return "SUCCEEDED";
        case ST_FAILED:    return "FAILED";
        case ST_EXPIRED:   return "EXPIRED";
        default:           return "?";
    }
}

const char *cmd_err_name(int32_t err) {
    switch (err) {
        case E_OK:           return "OK";
        case E_SHORT_FRAME:  return "SHORT_FRAME";
        case E_BAD_MAGIC:    return "BAD_MAGIC";
        case E_BAD_VERSION:  return "BAD_VERSION";
        case E_BAD_CRC:      return "BAD_CRC";
        case E_BAD_LENGTH:   return "BAD_LENGTH";
        case E_REPLAY:       return "REPLAY";
        case E_EXPIRED:      return "EXPIRED";
        case E_SUPERSEDED:   return "SUPERSEDED";
        case E_NO_SLOT:      return "NO_SLOT";
        case E_QUEUE_FULL:   return "QUEUE_FULL";
        case E_UNKNOWN_TYPE: return "UNKNOWN_TYPE";
        case E_BAD_PAYLOAD:  return "BAD_PAYLOAD";
        case E_SUPPLY_SAG:   return "SUPPLY_SAG";
        case E_STALL:        return "STALL";
        case E_POWER_RESET:  return "POWER_RESET";
        default:             return "?";
    }
}

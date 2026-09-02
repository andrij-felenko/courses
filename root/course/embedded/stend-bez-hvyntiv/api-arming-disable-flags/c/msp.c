#include "msp.h"

const char *msp_strerror(msp_err_t err)
{
    switch (err) {
    case MSP_OK:                  return "гаразд";
    case MSP_ERR_TOO_SHORT:       return "кадр коротший за шапку";
    case MSP_ERR_BAD_MAGIC:       return "немає префікса $M";
    case MSP_ERR_NOT_A_REPLY:     return "це не відповідь плати ('<' або '!')";
    case MSP_ERR_LENGTH:          return "довжина буфера не збігається з полем size";
    case MSP_ERR_CHECKSUM:        return "контрольна сума не збіглася";
    case MSP_ERR_UNEXPECTED_CODE: return "код повідомлення не MSP_STATUS";
    case MSP_ERR_TRUNCATED:       return "payload обірвано — прошивка віддала менше полів";
    }
    return "невідома помилка";
}

/* Читач із межами: після першого виходу за буфер усе решта віддає нулі,
 * а ok лишається false — перевіряти досить один раз у кінці. */
typedef struct {
    const uint8_t *p;
    size_t len;
    size_t pos;
    bool ok;
} reader_t;

static uint8_t rd_u8(reader_t *r)
{
    if (!r->ok || r->pos >= r->len) {
        r->ok = false;
        return 0;
    }
    return r->p[r->pos++];
}

static uint16_t rd_u16(reader_t *r)
{
    const uint16_t lo = rd_u8(r);
    const uint16_t hi = rd_u8(r);
    return (uint16_t)(lo | (uint16_t)(hi << 8));
}

static uint32_t rd_u32(reader_t *r)
{
    const uint32_t b0 = rd_u8(r);
    const uint32_t b1 = rd_u8(r);
    const uint32_t b2 = rd_u8(r);
    const uint32_t b3 = rd_u8(r);
    return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
}

size_t msp_build_request(uint8_t code, uint8_t *buf, size_t cap)
{
    if (cap < 6) {
        return 0;
    }
    buf[0] = '$';
    buf[1] = 'M';
    buf[2] = '<';
    buf[3] = 0;              /* payload порожній */
    buf[4] = code;
    buf[5] = (uint8_t)(0u ^ code);
    return 6;
}

msp_err_t msp_parse_status(const uint8_t *frame, size_t len, msp_status_t *out)
{
    if (len < 6) {
        return MSP_ERR_TOO_SHORT;
    }
    if (frame[0] != '$' || frame[1] != 'M') {
        return MSP_ERR_BAD_MAGIC;
    }
    if (frame[2] != '>') {
        return MSP_ERR_NOT_A_REPLY;
    }

    const uint8_t size = frame[3];
    const uint8_t code = frame[4];
    if (len != (size_t)size + 6u) {
        return MSP_ERR_LENGTH;
    }

    uint8_t crc = (uint8_t)(size ^ code);
    for (uint8_t i = 0; i < size; ++i) {
        crc ^= frame[5 + i];
    }
    if (crc != frame[5 + size]) {
        return MSP_ERR_CHECKSUM;
    }
    if (code != MSP_STATUS) {
        return MSP_ERR_UNEXPECTED_CODE;
    }

    reader_t r = { frame + 5, size, 0, true };
    msp_status_t s = { 0 };

    s.cycle_time_us = rd_u16(&r);
    s.i2c_errors = rd_u16(&r);
    s.sensors = rd_u16(&r);
    s.flight_mode_flags = rd_u32(&r);
    s.pid_profile = rd_u8(&r);
    s.cpu_load_pct = rd_u16(&r);
    s.gyro_cycle_time_us = rd_u16(&r);

    /* Довжина блоку додаткових BOX-прапорців змінна — без неї до маски
     * блокувань не дійти, і саме тут ламаються саморобні парсери. */
    s.extra_len = (uint8_t)(rd_u8(&r) & 0x0Fu);
    for (uint8_t i = 0; i < s.extra_len; ++i) {
        s.extra_mode_flags[i] = rd_u8(&r);
    }

    s.arming_flag_count = rd_u8(&r);
    s.arming_disable_flags = rd_u32(&r);
    s.config_state = rd_u8(&r);

    if (!r.ok) {
        return MSP_ERR_TRUNCATED;
    }

    *out = s;
    return MSP_OK;
}

size_t msp_encode_status(const msp_status_t *st, uint8_t *buf, size_t cap)
{
    uint8_t payload[64];
    size_t n = 0;

    const uint8_t extra = (st->extra_len > MSP_MAX_EXTRA) ? MSP_MAX_EXTRA : st->extra_len;

    payload[n++] = (uint8_t)(st->cycle_time_us & 0xFFu);
    payload[n++] = (uint8_t)(st->cycle_time_us >> 8);
    payload[n++] = (uint8_t)(st->i2c_errors & 0xFFu);
    payload[n++] = (uint8_t)(st->i2c_errors >> 8);
    payload[n++] = (uint8_t)(st->sensors & 0xFFu);
    payload[n++] = (uint8_t)(st->sensors >> 8);
    payload[n++] = (uint8_t)(st->flight_mode_flags & 0xFFu);
    payload[n++] = (uint8_t)((st->flight_mode_flags >> 8) & 0xFFu);
    payload[n++] = (uint8_t)((st->flight_mode_flags >> 16) & 0xFFu);
    payload[n++] = (uint8_t)((st->flight_mode_flags >> 24) & 0xFFu);
    payload[n++] = st->pid_profile;
    payload[n++] = (uint8_t)(st->cpu_load_pct & 0xFFu);
    payload[n++] = (uint8_t)(st->cpu_load_pct >> 8);
    payload[n++] = (uint8_t)(st->gyro_cycle_time_us & 0xFFu);
    payload[n++] = (uint8_t)(st->gyro_cycle_time_us >> 8);
    payload[n++] = extra;
    for (uint8_t i = 0; i < extra; ++i) {
        payload[n++] = st->extra_mode_flags[i];
    }
    payload[n++] = st->arming_flag_count;
    payload[n++] = (uint8_t)(st->arming_disable_flags & 0xFFu);
    payload[n++] = (uint8_t)((st->arming_disable_flags >> 8) & 0xFFu);
    payload[n++] = (uint8_t)((st->arming_disable_flags >> 16) & 0xFFu);
    payload[n++] = (uint8_t)((st->arming_disable_flags >> 24) & 0xFFu);
    payload[n++] = st->config_state;

    if (cap < n + 6) {
        return 0;
    }

    buf[0] = '$';
    buf[1] = 'M';
    buf[2] = '>';
    buf[3] = (uint8_t)n;
    buf[4] = MSP_STATUS;

    uint8_t crc = (uint8_t)((uint8_t)n ^ (uint8_t)MSP_STATUS);
    for (size_t i = 0; i < n; ++i) {
        buf[5 + i] = payload[i];
        crc ^= payload[i];
    }
    buf[5 + n] = crc;
    return n + 6;
}

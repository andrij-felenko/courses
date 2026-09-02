#include "telemetry_protocol.h"

/* Числа збираємо зсувами, а не приведенням вказівника на структуру:
   (proto_telemetry_t *)buf — це і порушення strict aliasing, і HardFault
   на Cortex-M0, щойно кадр ляже в буфер за непарною адресою. */
static uint16_t rd_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int16_t rd_s16(const uint8_t *p)
{
    uint16_t raw = rd_u16(p);
    /* Знак відновлюємо явно: звуження uint16_t -> int16_t для значень
       понад 0x7FFF до C23 було реалізаційно визначене. */
    return (raw & 0x8000u) ? (int16_t)((int32_t)raw - 0x10000) : (int16_t)raw;
}

static void wr_u16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)(v >> 8);
}

/* Довжина навантаження для типу; -1 — тип не наш. */
static int payload_len_of(proto_msg_id_t id)
{
    switch (id) {
    case MSG_CMD_PING:         return (int)PROTO_LEN_PING;
    case MSG_CMD_SET_CONFIG:   return (int)PROTO_LEN_SET_CONFIG;
    case MSG_TELEMETRY_REPORT: return (int)PROTO_LEN_TELEMETRY;
    case MSG_CMD_RESPONSE:     return (int)PROTO_LEN_ACK;
    default:                   return -1;
    }
}

float proto_temperature_c(const proto_telemetry_t *t)
{
    return (float)t->temp_raw * 0.01f;
}

float proto_pressure_hpa(const proto_telemetry_t *t)
{
    return (float)t->pressure_raw * 0.1f;
}

float proto_alert_threshold_c(const proto_set_config_t *c)
{
    return (float)c->alert_threshold_raw * 0.01f;
}

int proto_alert_active(const proto_telemetry_t *t)
{
    return (t->flags & PROTO_FLAG_ALERT) != 0;
}

int proto_sensor_fault(const proto_telemetry_t *t)
{
    return (t->flags & PROTO_FLAG_SENSOR_FAULT) != 0;
}

uint16_t proto_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

proto_status_t proto_parse_frame(const uint8_t *buf, size_t len, proto_frame_t *out)
{
    if (buf == NULL || out == NULL) {
        return ERR_BAD_ARG;
    }
    if (len < PROTO_MIN_FRAME_LEN) {
        return ERR_INVALID_LEN;
    }
    if (buf[0] != PROTO_SOF) {
        return ERR_INVALID_SOF;
    }
    if (buf[len - 1] != PROTO_EOF) {
        return ERR_INVALID_EOF;
    }

    /* Довжину беремо з заголовка й ЗВІРЯЄМО з фактичним розміром буфера,
       перш ніж торкатися навантаження: заявлені 8 байтів у чотирибайтовому
       кадрі — це не «дочитаємо», а вихід за межі. */
    uint16_t payload_len = rd_u16(&buf[4]);
    if (payload_len > PROTO_MAX_PAYLOAD ||
        len != (size_t)PROTO_HEADER_LEN + payload_len + PROTO_FOOTER_LEN) {
        return ERR_INVALID_LEN;
    }

    /* Суму перевіряємо раніше за версію й тип: до неї жодному полю кадру
       вірити не можна, а межі ми вже перевірили вище. */
    uint16_t expected_crc = rd_u16(&buf[PROTO_HEADER_LEN + payload_len]);
    uint16_t actual_crc = proto_crc16(&buf[1], (size_t)(PROTO_HEADER_LEN - 1) + payload_len);
    if (actual_crc != expected_crc) {
        return ERR_INVALID_CRC;
    }

    if (buf[1] != PROTO_VERSION) {
        return ERR_UNSUPPORTED_VERSION;
    }

    proto_msg_id_t msg_id = (proto_msg_id_t)buf[2];
    int expect_len = payload_len_of(msg_id);
    if (expect_len < 0) {
        /* Пакет майбутньої версії протоколу: штатна відмова, не падіння. */
        return ERR_UNKNOWN_MSG;
    }
    if ((uint16_t)expect_len != payload_len) {
        /* Схема таку невідповідність не ловить — це робота застосунку. */
        return ERR_INVALID_LEN;
    }

    out->version = buf[1];
    out->msg_id = msg_id;
    out->seq_id = buf[3];

    const uint8_t *p = &buf[PROTO_HEADER_LEN];
    switch (msg_id) {
    case MSG_CMD_PING:
        break;
    case MSG_CMD_SET_CONFIG:
        out->payload.set_config.sample_rate_hz = rd_u16(&p[0]);
        out->payload.set_config.alert_threshold_raw = rd_s16(&p[2]);
        out->payload.set_config.flags_enable = p[4];
        break;
    case MSG_TELEMETRY_REPORT:
        out->payload.telemetry.temp_raw = rd_s16(&p[0]);
        out->payload.telemetry.pressure_raw = rd_u16(&p[2]);
        out->payload.telemetry.voltage_mv = rd_u16(&p[4]);
        out->payload.telemetry.flags = p[6];
        out->payload.telemetry.reserved = p[7];
        break;
    case MSG_CMD_RESPONSE:
        /* Невідомий код статусу не валимо: інша сторона могла піти вперед
           у словнику помилок, і це не привід відкидати цілий кадр. */
        out->payload.ack.target_seq_id = p[0];
        out->payload.ack.status = (proto_status_code_t)p[1];
        break;
    }

    return STATUS_OK;
}

size_t proto_build_frame(const proto_frame_t *in, uint8_t *out, size_t out_cap)
{
    if (in == NULL || out == NULL) {
        return 0;
    }
    int payload_len = payload_len_of(in->msg_id);
    if (payload_len < 0) {
        return 0;
    }
    size_t total = PROTO_HEADER_LEN + (size_t)payload_len + PROTO_FOOTER_LEN;
    if (out_cap < total) {
        return 0;
    }

    out[0] = (uint8_t)PROTO_SOF;
    out[1] = (uint8_t)PROTO_VERSION;
    out[2] = (uint8_t)in->msg_id;
    out[3] = in->seq_id;
    wr_u16(&out[4], (uint16_t)payload_len);

    uint8_t *p = &out[PROTO_HEADER_LEN];
    switch (in->msg_id) {
    case MSG_CMD_PING:
        break;
    case MSG_CMD_SET_CONFIG:
        wr_u16(&p[0], in->payload.set_config.sample_rate_hz);
        wr_u16(&p[2], (uint16_t)in->payload.set_config.alert_threshold_raw);
        p[4] = in->payload.set_config.flags_enable;
        break;
    case MSG_TELEMETRY_REPORT:
        wr_u16(&p[0], (uint16_t)in->payload.telemetry.temp_raw);
        wr_u16(&p[2], in->payload.telemetry.pressure_raw);
        wr_u16(&p[4], in->payload.telemetry.voltage_mv);
        p[6] = in->payload.telemetry.flags;
        p[7] = in->payload.telemetry.reserved;
        break;
    case MSG_CMD_RESPONSE:
        p[0] = in->payload.ack.target_seq_id;
        p[1] = (uint8_t)in->payload.ack.status;
        break;
    }

    wr_u16(&out[PROTO_HEADER_LEN + payload_len],
           proto_crc16(&out[1], (size_t)(PROTO_HEADER_LEN - 1) + (size_t)payload_len));
    out[total - 1] = (uint8_t)PROTO_EOF;
    return total;
}

const char *proto_status_str(proto_status_t st)
{
    switch (st) {
    case STATUS_OK:               return "STATUS_OK";
    case ERR_INVALID_SOF:         return "ERR_INVALID_SOF";
    case ERR_INVALID_EOF:         return "ERR_INVALID_EOF";
    case ERR_INVALID_LEN:         return "ERR_INVALID_LEN";
    case ERR_INVALID_CRC:         return "ERR_INVALID_CRC";
    case ERR_UNKNOWN_MSG:         return "ERR_UNKNOWN_MSG";
    case ERR_UNSUPPORTED_VERSION: return "ERR_UNSUPPORTED_VERSION";
    case ERR_BAD_ARG:             return "ERR_BAD_ARG";
    }
    return "ERR_???";
}

const char *proto_status_code_str(proto_status_code_t code)
{
    switch (code) {
    case STATUS_CODE_OK:                      return "ok";
    case STATUS_CODE_INVALID_CRC:             return "invalid_crc";
    case STATUS_CODE_UNKNOWN_CMD:             return "unknown_cmd";
    case STATUS_CODE_PAYLOAD_LENGTH_MISMATCH: return "payload_length_mismatch";
    case STATUS_CODE_PARAM_OUT_OF_RANGE:      return "param_out_of_range";
    case STATUS_CODE_HARDWARE_BUSY:           return "hardware_busy";
    }
    return "unknown_status";
}

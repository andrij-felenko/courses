#ifndef TELEMETRY_PROTOCOL_H
#define TELEMETRY_PROTOCOL_H

/* Ручний нуль-копіювальний кодек кадру telemetry_protocol.ksy.
   Схема лишається єдиним джерелом правди: усі довжини, зсуви й коди
   нижче переписані з неї один в один, а не вигадані тут. */

#include <stddef.h>
#include <stdint.h>

#define PROTO_SOF     0xAAu
#define PROTO_EOF     0x55u
#define PROTO_VERSION 0x01u

/* sof, version, msg_id, seq_id, payload_len(2) */
#define PROTO_HEADER_LEN 6u
/* crc16(2), eof */
#define PROTO_FOOTER_LEN 3u
#define PROTO_MIN_FRAME_LEN (PROTO_HEADER_LEN + PROTO_FOOTER_LEN)

/* Стеля навантаження вузла: більший кадр приймати нема куди й нема навіщо. */
#define PROTO_MAX_PAYLOAD 64u
#define PROTO_MAX_FRAME (PROTO_HEADER_LEN + PROTO_MAX_PAYLOAD + PROTO_FOOTER_LEN)

/* Довжини навантажень за схемою. Саме константи, а не sizeof структури:
   sizeof залежить від вирівнювання компілятора, а формат на дроті — ні. */
#define PROTO_LEN_PING        0u
#define PROTO_LEN_SET_CONFIG  5u
#define PROTO_LEN_TELEMETRY   8u
#define PROTO_LEN_ACK         2u

/* Біти поля flags у msg_telemetry (instances alert_active / sensor_fault). */
#define PROTO_FLAG_ALERT        0x01u
#define PROTO_FLAG_SENSOR_FAULT 0x02u

/* Результат розбору кадру — це не status_code зі схеми: там коди для
   відповіді іншій стороні, тут — діагностика власного парсера. */
typedef enum {
    STATUS_OK = 0,
    ERR_INVALID_SOF,
    ERR_INVALID_EOF,
    ERR_INVALID_LEN,
    ERR_INVALID_CRC,
    ERR_UNKNOWN_MSG,
    ERR_UNSUPPORTED_VERSION,
    ERR_BAD_ARG
} proto_status_t;

/* enums::msg_type */
typedef enum {
    MSG_CMD_PING = 0x01,
    MSG_CMD_SET_CONFIG = 0x02,
    MSG_TELEMETRY_REPORT = 0x20,
    MSG_CMD_RESPONSE = 0x80
} proto_msg_id_t;

/* enums::status_code — їде в полі status повідомлення cmd_response */
typedef enum {
    STATUS_CODE_OK = 0x00,
    STATUS_CODE_INVALID_CRC = 0x01,
    STATUS_CODE_UNKNOWN_CMD = 0x02,
    STATUS_CODE_PAYLOAD_LENGTH_MISMATCH = 0x03,
    STATUS_CODE_PARAM_OUT_OF_RANGE = 0x04,
    STATUS_CODE_HARDWARE_BUSY = 0x05
} proto_status_code_t;

/* types::msg_telemetry */
typedef struct {
    int16_t  temp_raw;
    uint16_t pressure_raw;
    uint16_t voltage_mv;
    uint8_t  flags;
    uint8_t  reserved;
} proto_telemetry_t;

/* types::msg_set_config */
typedef struct {
    uint16_t sample_rate_hz;
    int16_t  alert_threshold_raw;
    uint8_t  flags_enable;
} proto_set_config_t;

/* types::msg_ack_response */
typedef struct {
    uint8_t             target_seq_id;
    proto_status_code_t status;
} proto_ack_t;

/* Аналог switch-on зі схеми: тип навантаження вибирає msg_id. */
typedef struct {
    uint8_t        version;
    proto_msg_id_t msg_id;
    uint8_t        seq_id;
    union {
        proto_telemetry_t  telemetry;
        proto_set_config_t set_config;
        proto_ack_t        ack;
    } payload;
} proto_frame_t;

/* instances зі схеми: сирий код датчика у фізичну величину.
   На дроті float немає — множення живе тільки тут. */
float proto_temperature_c(const proto_telemetry_t *t);
float proto_pressure_hpa(const proto_telemetry_t *t);
float proto_alert_threshold_c(const proto_set_config_t *c);
int   proto_alert_active(const proto_telemetry_t *t);
int   proto_sensor_fault(const proto_telemetry_t *t);

/* CRC-16/CCITT-FALSE: поліном 0x1021, init 0xFFFF, без відображення бітів. */
uint16_t proto_crc16(const uint8_t *data, size_t len);

/* Розбирає кадр із буфера. Нічого не виділяє й нічого не зберігає між викликами. */
proto_status_t proto_parse_frame(const uint8_t *buf, size_t len, proto_frame_t *out);

/* Збирає кадр у out. Повертає довжину або 0, якщо тип невідомий чи місця мало. */
size_t proto_build_frame(const proto_frame_t *in, uint8_t *out, size_t out_cap);

const char *proto_status_str(proto_status_t st);
const char *proto_status_code_str(proto_status_code_t code);

#endif /* TELEMETRY_PROTOCOL_H */

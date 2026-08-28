// Реалізація трьох методів пакування телеметрії для вбудованих систем (C99)
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// 1. Корисні дані датчика
typedef struct {
    uint32_t timestamp_s;  // Unix час (секунди)
    int16_t  temp_centi_c; // Температура, 2550 = 25.50 °C
    uint16_t humidity_pct; // Вологість, 6020 = 60.20 %
    uint16_t vbat_mv;      // Напруга батареї, 3280 = 3.28 В
} telemetry_sample_t;

// -----------------------------------------------------------------------------
// Підхід 1: Формування HTTP POST запиту з JSON-тілом
// -----------------------------------------------------------------------------
size_t build_http_post_request(const telemetry_sample_t *s,
                               const char *host,
                               const char *token,
                               char *out_buf,
                               size_t max_len)
{
    char json_payload[128];
    int json_len = snprintf(json_payload, sizeof(json_payload),
        "{\"ts\":%lu,\"t\":%.2f,\"h\":%.2f,\"vbat\":%u}",
        (unsigned long)s->timestamp_s,
        (double)s->temp_centi_c / 100.0,
        (double)s->humidity_pct / 100.0,
        (unsigned int)s->vbat_mv);

    if (json_len < 0 || (size_t)json_len >= sizeof(json_payload)) {
        return 0; // Помилка форматування
    }

    int http_len = snprintf(out_buf, max_len,
        "POST /api/v1/telemetry HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Authorization: Bearer %s\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        host, token, json_len, json_payload);

    if (http_len < 0 || (size_t)http_len >= max_len) {
        return 0;
    }
    return (size_t)http_len;
}

// -----------------------------------------------------------------------------
// Підхід 2: Формування MQTT 3.1.1 PUBLISH пакета (QoS 1)
// -----------------------------------------------------------------------------
size_t build_mqtt_publish_qos1(const telemetry_sample_t *s,
                               const char *topic,
                               uint16_t packet_id,
                               uint8_t *out_buf,
                               size_t max_len)
{
    char payload[64];
    int payload_len = snprintf(payload, sizeof(payload),
        "{\"t\":%d,\"h\":%u,\"v\":%u}",
        s->temp_centi_c, s->humidity_pct, s->vbat_mv);

    if (payload_len < 0) return 0;

    size_t topic_len = strlen(topic);
    // Змінний заголовок: Topic Length (2 B) + Topic + Packet ID (2 B для QoS 1)
    size_t var_header_len = 2 + topic_len + 2;
    size_t remaining_len = var_header_len + (size_t)payload_len;

    // Фіксований заголовок: 0x32 (PUBLISH, QoS=1, DUP=0, RETAIN=0) + Remaining Length
    // Спрощене кодування довжини (1 байт, якщо < 128)
    if (remaining_len > 127 || (2 + remaining_len) > max_len) {
        return 0;
    }

    size_t idx = 0;
    out_buf[idx++] = 0x32; // PUBLISH QoS 1
    out_buf[idx++] = (uint8_t)remaining_len;

    // Topic Length (Big Endian)
    out_buf[idx++] = (uint8_t)(topic_len >> 8);
    out_buf[idx++] = (uint8_t)(topic_len & 0xFF);
    memcpy(&out_buf[idx], topic, topic_len);
    idx += topic_len;

    // Packet Identifier (Big Endian)
    out_buf[idx++] = (uint8_t)(packet_id >> 8);
    out_buf[idx++] = (uint8_t)(packet_id & 0xFF);

    // Payload
    memcpy(&out_buf[idx], payload, (size_t)payload_len);
    idx += (size_t)payload_len;

    return idx;
}

// -----------------------------------------------------------------------------
// Підхід 3: Власний бінарний кадр з фіксованою структурою та CRC-16
// -----------------------------------------------------------------------------
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       // 0xAA (синхробайтер)
    uint8_t  msg_type;    // 0x01 = Телеметрія сенсорів
    uint16_t seq_num;     // Лічильник пакета (захист від втрат і дублів)
    uint32_t timestamp_s; // Час або uptime
    int16_t  temp_c;      // 25.50 °C
    uint16_t hum_pct;     // 60.20 %
    uint16_t vbat_mv;     // 3280 мВ
    uint16_t crc16;       // Контрольна сума CRC-16-CCITT
} custom_frame_t;
#pragma pack(pop)

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

size_t build_custom_binary_frame(const telemetry_sample_t *s,
                                 uint16_t seq,
                                 uint8_t *out_buf,
                                 size_t max_len)
{
    if (max_len < sizeof(custom_frame_t)) {
        return 0;
    }

    custom_frame_t frame;
    frame.magic = 0xAA;
    frame.msg_type = 0x01;
    frame.seq_num = seq;
    frame.timestamp_s = s->timestamp_s;
    frame.temp_c = s->temp_centi_c;
    frame.hum_pct = s->humidity_pct;
    frame.vbat_mv = s->vbat_mv;

    // Рахуємо CRC без останнього 2-байтового поля crc16
    size_t payload_len = sizeof(custom_frame_t) - sizeof(uint16_t);
    frame.crc16 = crc16_ccitt((const uint8_t *)&frame, payload_len);

    memcpy(out_buf, &frame, sizeof(custom_frame_t));
    return sizeof(custom_frame_t);
}

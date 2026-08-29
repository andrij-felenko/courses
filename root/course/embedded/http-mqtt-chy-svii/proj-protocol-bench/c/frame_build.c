// Три способи покласти ті самі 10 байтів вимірів у мережу (C99).
#include "telemetry.h"

#include <stdio.h>
#include <string.h>

uint16_t crc16_ccitt(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000u) {
                crc = (uint16_t)((crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

// -----------------------------------------------------------------------------
// Підхід 1: HTTP/1.1 POST із JSON-тілом
// -----------------------------------------------------------------------------
size_t build_http_post_request(const telemetry_sample_t *s,
                               const char *host,
                               const char *token,
                               char *out_buf,
                               size_t max_len)
{
    if (s == NULL || host == NULL || token == NULL || out_buf == NULL || max_len == 0) {
        return 0;
    }

    // Перший буфер: тіло. Воно потрібне цілком і заздалегідь, бо його довжину
    // треба написати в Content-Length — тобто в заголовок, який іде ПЕРЕД тілом.
    // Звідси й два буфери на стеку замість одного потоку байтів.
    char json_payload[128];
    int json_len = snprintf(json_payload, sizeof(json_payload),
        "{\"ts\":%lu,\"t\":%.2f,\"h\":%.2f,\"vbat\":%u}",
        (unsigned long)s->timestamp_s,
        (double)s->temp_centi_c / 100.0,
        (double)s->humidity_pct / 100.0,
        (unsigned int)s->vbat_mv);
    // Саме цей рядок коштує близько 4000 тактів: %.2f тягне за собою
    // програмну арифметику з плаваючою комою (на Cortex-M4 без FPU-підтримки
    // в бібліотеці — то ділення в циклі). Дешевша заміна для цілих сотих —
    // "%d.%02d" з окремими цілою й дробовою частинами, але з відʼємною
    // температурою її треба писати обережно: -5 сотих це "-0.05", а не "0.-5".
    if (json_len < 0 || (size_t)json_len >= sizeof(json_payload)) {
        return 0;
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

    // snprintf обрізає тихо й повертає довжину, яка БУЛА Б потрібна, — саме
    // тому порівнюємо з max_len, а не радіємо ненульовому результату.
    if (http_len < 0 || (size_t)http_len >= max_len) {
        return 0;
    }
    return (size_t)http_len;
}

// -----------------------------------------------------------------------------
// Підхід 2: MQTT 3.1.1 PUBLISH з QoS 1
// -----------------------------------------------------------------------------

// Remaining Length у MQTT — це не байт, а змінне кодування по 7 біт на байт:
// старший біт каже «є продовження». 127 байтів кодуються одним байтом,
// 16 383 — двома, і так до чотирьох байтів (268 435 455).
// Повертає кількість записаних байтів або 0, якщо довжина завелика.
static size_t mqtt_encode_remaining_length(uint8_t *out, size_t remaining)
{
    if (remaining > 268435455u) {
        return 0;
    }
    size_t n = 0;
    do {
        uint8_t digit = (uint8_t)(remaining % 128u);
        remaining /= 128u;
        if (remaining > 0) {
            digit |= 0x80u;   // прапорець «далі ще байт»
        }
        out[n++] = digit;
    } while (remaining > 0);
    return n;
}

size_t build_mqtt_publish_qos1(const telemetry_sample_t *s,
                               const char *topic,
                               uint16_t packet_id,
                               uint8_t *out_buf,
                               size_t max_len)
{
    if (s == NULL || topic == NULL || out_buf == NULL) {
        return 0;
    }
    // Packet Identifier 0 заборонений специфікацією для QoS 1: брокер не
    // зможе підтвердити такий пакет через PUBACK.
    if (packet_id == 0) {
        return 0;
    }

    size_t topic_len = strlen(topic);
    if (topic_len == 0 || topic_len > 0xFFFFu) {
        return 0;
    }
    // Публікувати можна лише в конкретну тему: шаблони '+' і '#' — це
    // синтаксис підписки, брокер розірве зʼєднання за таку тему в PUBLISH.
    for (size_t i = 0; i < topic_len; i++) {
        if (topic[i] == '+' || topic[i] == '#') {
            return 0;
        }
    }

    char payload[64];
    int payload_len = snprintf(payload, sizeof(payload),
        "{\"t\":%d,\"h\":%u,\"v\":%u}",
        (int)s->temp_centi_c,
        (unsigned int)s->humidity_pct,
        (unsigned int)s->vbat_mv);
    if (payload_len < 0 || (size_t)payload_len >= sizeof(payload)) {
        return 0;
    }

    // Змінний заголовок: довжина теми (2 Б) + тема + Packet ID (2 Б для QoS 1).
    size_t var_header_len = 2u + topic_len + 2u;
    size_t remaining_len = var_header_len + (size_t)payload_len;

    uint8_t len_bytes[4];
    size_t len_bytes_n = mqtt_encode_remaining_length(len_bytes, remaining_len);
    if (len_bytes_n == 0) {
        return 0;
    }
    if (1u + len_bytes_n + remaining_len > max_len) {
        return 0;
    }

    size_t idx = 0;
    out_buf[idx++] = 0x32u;   // PUBLISH, DUP=0, QoS=1, RETAIN=0
    memcpy(&out_buf[idx], len_bytes, len_bytes_n);
    idx += len_bytes_n;

    // Довжина теми — big-endian, як усі 16-бітні поля MQTT.
    out_buf[idx++] = (uint8_t)(topic_len >> 8);
    out_buf[idx++] = (uint8_t)(topic_len & 0xFFu);
    memcpy(&out_buf[idx], topic, topic_len);
    idx += topic_len;

    out_buf[idx++] = (uint8_t)(packet_id >> 8);
    out_buf[idx++] = (uint8_t)(packet_id & 0xFFu);

    memcpy(&out_buf[idx], payload, (size_t)payload_len);
    idx += (size_t)payload_len;

    return idx;
}

// -----------------------------------------------------------------------------
// Підхід 3: власний бінарний кадр із CRC-16
// -----------------------------------------------------------------------------
size_t build_custom_binary_frame(const telemetry_sample_t *s,
                                 uint16_t seq,
                                 uint8_t *out_buf,
                                 size_t max_len)
{
    if (s == NULL || out_buf == NULL || max_len < sizeof(custom_frame_t)) {
        return 0;
    }

    // Обнуляємо все поле кадру перед заповненням. Структура запакована й
    // проміжків не має, але звичка обовʼязкова: щойно хтось додасть поле й
    // забуде його заповнити, у CRC поїде вміст стека — а це помилка, що
    // ловиться раз на сотню кадрів і виглядає як завади в ефірі.
    custom_frame_t frame;
    memset(&frame, 0, sizeof(frame));

    frame.magic       = FRAME_MAGIC;
    frame.msg_type    = FRAME_TYPE_TELEM;
    frame.seq_num     = seq;
    frame.timestamp_s = s->timestamp_s;
    frame.temp_c      = s->temp_centi_c;
    frame.hum_pct     = s->humidity_pct;
    frame.vbat_mv     = s->vbat_mv;

    // CRC рахуємо по всьому кадру, крім самого поля crc16 у хвості.
    frame.crc16 = crc16_ccitt((const uint8_t *)&frame, CUSTOM_FRAME_CRC_LEN);

    memcpy(out_buf, &frame, sizeof(frame));
    return sizeof(frame);
}

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define MQTT_PKT_CONNECT 0x10
#define MQTT_PKT_PUBLISH 0x30

/* Кодування поля змінної довжини (Remaining Length) */
static size_t mqtt_encode_remaining_length(uint8_t *buf, size_t length) {
    size_t bytes = 0;
    do {
        uint8_t byte = (uint8_t)(length & 0x7F);
        length >>= 7;
        if (length > 0) {
            byte |= 0x80;
        }
        buf[bytes++] = byte;
    } while (length > 0);
    return bytes;
}

/* Допоміжна функція запису UTF-8 рядка з двобайтним префіксом довжини */
static size_t mqtt_write_string(uint8_t *buf, const char *str) {
    size_t len = strlen(str);
    buf[0] = (uint8_t)((len >> 8) & 0xFF);
    buf[1] = (uint8_t)(len & 0xFF);
    memcpy(&buf[2], str, len);
    return len + 2;
}

typedef struct {
    const char *client_id;
    uint16_t    keep_alive_sec;
    bool        clean_session;
    struct {
        const char *topic;
        const char *message;
        uint8_t     qos;
        bool        retain;
    } will;
} mqtt_connect_params_t;

/* Генерація пакета CONNECT з реєстрацією LWT */
size_t mqtt_pack_connect(uint8_t *out_buf, size_t max_buf_size,
                         const mqtt_connect_params_t *params) {
    if (!out_buf || !params || !params->client_id) return 0;

    uint8_t payload[256];
    size_t payload_len = 0;

    /* Variable Header: Protocol Name ("MQTT"), Level (4 = v3.1.1), Flags, KeepAlive */
    uint8_t var_header[10];
    var_header[0] = 0x00;
    var_header[1] = 0x04;
    var_header[2] = 'M';
    var_header[3] = 'Q';
    var_header[4] = 'T';
    var_header[5] = 'T';
    var_header[6] = 0x04; /* MQTT v3.1.1 */

    uint8_t flags = 0;
    if (params->clean_session) flags |= 0x02;

    /* Payload: Client ID обов'язковий */
    payload_len += mqtt_write_string(&payload[payload_len], params->client_id);

    /* Заповіт LWT */
    if (params->will.topic && params->will.message) {
        flags |= 0x04; /* Will Flag */
        flags |= (uint8_t)((params->will.qos & 0x03) << 3);
        if (params->will.retain) flags |= 0x20;

        payload_len += mqtt_write_string(&payload[payload_len], params->will.topic);
        payload_len += mqtt_write_string(&payload[payload_len], params->will.message);
    }

    var_header[7] = flags;
    var_header[8] = (uint8_t)((params->keep_alive_sec >> 8) & 0xFF);
    var_header[9] = (uint8_t)(params->keep_alive_sec & 0xFF);

    size_t rem_len = sizeof(var_header) + payload_len;
    uint8_t rem_len_bytes[4];
    size_t rem_len_size = mqtt_encode_remaining_length(rem_len_bytes, rem_len);

    size_t total_size = 1 + rem_len_size + rem_len;
    if (total_size > max_buf_size) return 0;

    out_buf[0] = MQTT_PKT_CONNECT;
    memcpy(&out_buf[1], rem_len_bytes, rem_len_size);
    memcpy(&out_buf[1 + rem_len_size], var_header, sizeof(var_header));
    memcpy(&out_buf[1 + rem_len_size + sizeof(var_header)], payload, payload_len);

    return total_size;
}

/* Генерація пакета PUBLISH з вибором QoS та Retain */
size_t mqtt_pack_publish(uint8_t *out_buf, size_t max_buf_size,
                         const char *topic, const uint8_t *payload,
                         size_t payload_len, uint8_t qos, bool retain,
                         uint16_t packet_id) {
    if (!out_buf || !topic || (qos > 0 && packet_id == 0)) return 0;

    size_t topic_len = strlen(topic);
    size_t var_header_len = 2 + topic_len + (qos > 0 ? 2 : 0);
    size_t rem_len = var_header_len + payload_len;

    uint8_t rem_len_bytes[4];
    size_t rem_len_size = mqtt_encode_remaining_length(rem_len_bytes, rem_len);

    size_t total_size = 1 + rem_len_size + rem_len;
    if (total_size > max_buf_size) return 0;

    /* Fixed Header: тип повідомлення, DUP=0, QoS, Retain */
    out_buf[0] = (uint8_t)(MQTT_PKT_PUBLISH | ((qos & 0x03) << 1) | (retain ? 0x01 : 0x00));
    memcpy(&out_buf[1], rem_len_bytes, rem_len_size);

    size_t offset = 1 + rem_len_size;

    /* Variable Header: Topic Name */
    out_buf[offset++] = (uint8_t)((topic_len >> 8) & 0xFF);
    out_buf[offset++] = (uint8_t)(topic_len & 0xFF);
    memcpy(&out_buf[offset], topic, topic_len);
    offset += topic_len;

    /* Packet Identifier потрібен лише для QoS > 0 */
    if (qos > 0) {
        out_buf[offset++] = (uint8_t)((packet_id >> 8) & 0xFF);
        out_buf[offset++] = (uint8_t)(packet_id & 0xFF);
    }

    /* Payload */
    if (payload && payload_len > 0) {
        memcpy(&out_buf[offset], payload, payload_len);
        offset += payload_len;
    }

    return offset;
}

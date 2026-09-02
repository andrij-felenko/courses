#include "mqtt_min.h"

#include <string.h>

enum { PHASE_HEADER = 0, PHASE_LENGTH, PHASE_BODY };

static size_t varint_size(uint32_t n)
{
    if (n < 128u) {
        return 1u;
    }
    return (n < 16384u) ? 2u : 3u;
}

static size_t varint_put(uint8_t *p, uint32_t n)
{
    size_t i = 0;
    do {
        uint8_t digit = (uint8_t)(n % 128u);
        n /= 128u;
        if (n != 0u) {
            digit |= 0x80u;
        }
        p[i++] = digit;
    } while (n != 0u);
    return i;
}

/* Рядок MQTT: два байти довжини (big-endian) і тіло. */
static size_t str_put(uint8_t *p, const char *s)
{
    size_t n = strlen(s);
    p[0] = (uint8_t)(n >> 8);
    p[1] = (uint8_t)(n & 0xFFu);
    memcpy(p + 2, s, n);
    return n + 2u;
}

size_t mqtt_connect(uint8_t *buf, size_t cap, const char *client_id,
                    const char *user, const char *pass, uint16_t keepalive_s)
{
    uint8_t flags = 0x02u; /* Clean Session */
    size_t payload = 2u + strlen(client_id);

    if (user != NULL && user[0] != '\0') {
        flags |= 0x80u;
        payload += 2u + strlen(user);
    }
    if (pass != NULL && pass[0] != '\0') {
        flags |= 0x40u;
        payload += 2u + strlen(pass);
    }

    uint32_t remaining = (uint32_t)(10u + payload); /* 10 = "MQTT" + рівень + прапорці + keep-alive */
    if (1u + varint_size(remaining) + remaining > cap) {
        return 0;
    }

    size_t i = 0;
    buf[i++] = 0x10u; /* CONNECT */
    i += varint_put(buf + i, remaining);
    i += str_put(buf + i, "MQTT");
    buf[i++] = 0x04u; /* рівень протоколу 3.1.1 */
    buf[i++] = flags;
    buf[i++] = (uint8_t)(keepalive_s >> 8);
    buf[i++] = (uint8_t)(keepalive_s & 0xFFu);
    i += str_put(buf + i, client_id);
    if ((flags & 0x80u) != 0u) {
        i += str_put(buf + i, user);
    }
    if ((flags & 0x40u) != 0u) {
        i += str_put(buf + i, pass);
    }
    return i;
}

size_t mqtt_publish_qos1(uint8_t *buf, size_t cap, const char *topic,
                         const uint8_t *payload, size_t len, uint16_t packet_id)
{
    uint32_t remaining = (uint32_t)(2u + strlen(topic) + 2u + len);
    if (1u + varint_size(remaining) + remaining > cap) {
        return 0;
    }

    size_t i = 0;
    buf[i++] = 0x32u; /* PUBLISH, QoS 1 — брокер мусить відповісти PUBACK */
    i += varint_put(buf + i, remaining);
    i += str_put(buf + i, topic);
    buf[i++] = (uint8_t)(packet_id >> 8);
    buf[i++] = (uint8_t)(packet_id & 0xFFu);
    memcpy(buf + i, payload, len);
    return i + len;
}

size_t mqtt_pingreq(uint8_t *buf, size_t cap)
{
    if (cap < 2u) {
        return 0;
    }
    buf[0] = 0xC0u;
    buf[1] = 0x00u;
    return 2u;
}

size_t mqtt_disconnect(uint8_t *buf, size_t cap)
{
    if (cap < 2u) {
        return 0;
    }
    buf[0] = 0xE0u;
    buf[1] = 0x00u;
    return 2u;
}

void mqtt_rx_init(mqtt_rx_t *rx)
{
    memset(rx, 0, sizeof(*rx));
    rx->multiplier = 1u;
}

static void emit(const mqtt_rx_t *rx, mqtt_pkt_t *out)
{
    out->code = 0;
    out->packet_id = 0;

    switch (rx->header & 0xF0u) {
    case 0x20u:
        out->kind = MQTT_PKT_CONNACK;
        out->code = (rx->body_len >= 2u) ? rx->body[1] : 0xFFu;
        break;
    case 0x40u:
        out->kind = MQTT_PKT_PUBACK;
        if (rx->body_len >= 2u) {
            out->packet_id = (uint16_t)(((uint16_t)rx->body[0] << 8) | rx->body[1]);
        }
        break;
    case 0xD0u:
        out->kind = MQTT_PKT_PINGRESP;
        break;
    default:
        /* Наприклад PUBLISH від брокера: вузол ні на що не підписаний. */
        out->kind = MQTT_PKT_OTHER;
        break;
    }
}

bool mqtt_rx_byte(mqtt_rx_t *rx, uint8_t byte, mqtt_pkt_t *out)
{
    switch (rx->phase) {
    case PHASE_HEADER:
        rx->header = byte;
        rx->remaining = 0u;
        rx->multiplier = 1u;
        rx->len_bytes = 0u;
        rx->body_len = 0u;
        rx->phase = PHASE_LENGTH;
        return false;

    case PHASE_LENGTH:
        rx->remaining += (uint32_t)(byte & 0x7Fu) * rx->multiplier;
        rx->multiplier *= 128u;
        if (++rx->len_bytes > 4u) { /* довжина не буває довшою за 4 байти */
            mqtt_rx_init(rx);
            out->kind = MQTT_PKT_BROKEN;
            out->code = 0;
            out->packet_id = 0;
            return true;
        }
        if ((byte & 0x80u) != 0u) {
            return false;
        }
        if (rx->remaining == 0u) {
            emit(rx, out);
            mqtt_rx_init(rx);
            return true;
        }
        rx->phase = PHASE_BODY;
        return false;

    default:
        if (rx->body_len < sizeof(rx->body)) {
            rx->body[rx->body_len++] = byte; /* довгі тіла нам не потрібні */
        }
        if (--rx->remaining == 0u) {
            emit(rx, out);
            mqtt_rx_init(rx);
            return true;
        }
        return false;
    }
}

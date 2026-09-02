#ifndef MQTT_MIN_H
#define MQTT_MIN_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Мінімум MQTT 3.1.1, якого вистачає вузлу телеметрії: CONNECT/CONNACK,
   PUBLISH QoS 1/PUBACK, PINGREQ/PINGRESP, DISCONNECT. Байти кадру віддаємо
   в сокет самі — модем нічого про протокол додатків не знає. */

/* Усі складачі повертають довжину кадру або 0, якщо він не влазить у buf. */
size_t mqtt_connect(uint8_t *buf, size_t cap, const char *client_id,
                    const char *user, const char *pass, uint16_t keepalive_s);
size_t mqtt_publish_qos1(uint8_t *buf, size_t cap, const char *topic,
                         const uint8_t *payload, size_t len, uint16_t packet_id);
size_t mqtt_pingreq(uint8_t *buf, size_t cap);
size_t mqtt_disconnect(uint8_t *buf, size_t cap);

typedef enum {
    MQTT_PKT_CONNACK = 0,
    MQTT_PKT_PUBACK,
    MQTT_PKT_PINGRESP,
    MQTT_PKT_OTHER,
    MQTT_PKT_BROKEN /* потік не схожий на MQTT — сокет треба перевідкрити */
} mqtt_pkt_kind_t;

typedef struct {
    mqtt_pkt_kind_t kind;
    uint8_t         code;      /* код повернення CONNACK */
    uint16_t        packet_id; /* ідентифікатор PUBACK */
} mqtt_pkt_t;

typedef struct {
    uint8_t  phase;
    uint8_t  header;
    uint32_t remaining;
    uint32_t multiplier;
    uint8_t  len_bytes;
    uint8_t  body[8];
    uint8_t  body_len;
} mqtt_rx_t;

void mqtt_rx_init(mqtt_rx_t *rx);

/* Згодовує один байт; true → у *out зібраний пакет. */
bool mqtt_rx_byte(mqtt_rx_t *rx, uint8_t byte, mqtt_pkt_t *out);

#endif /* MQTT_MIN_H */

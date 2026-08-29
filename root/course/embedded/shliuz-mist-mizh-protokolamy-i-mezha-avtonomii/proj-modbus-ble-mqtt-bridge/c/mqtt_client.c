#define _GNU_SOURCE

#include "mqtt_client.h"

#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define MQTT_CONNECT     0x10
#define MQTT_CONNACK     0x20
#define MQTT_PUBLISH     0x30
#define MQTT_PUBACK      0x40
#define MQTT_PINGREQ     0xC0
#define MQTT_PINGRESP    0xD0
#define MQTT_DISCONNECT  0xE0

#define MQTT_MAX_PACKET  1024
#define CONNECT_TIMEOUT_MS 5000
#define ACK_TIMEOUT_MS     5000

struct mqtt_client {
    int fd;
    uint16_t next_pid;
    uint16_t keepalive_s;
    int64_t last_tx_ms;
    int64_t ping_deadline_ms;
    bool awaiting_pingresp;
};

static int64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static bool write_all(int fd, const uint8_t *buf, size_t len)
{
    size_t off = 0;
    while (off < len) {
        ssize_t n = write(fd, buf + off, len - off);
        if (n > 0) {
            off += (size_t)n;
            continue;
        }
        if (n < 0 && errno == EINTR)
            continue;
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            struct pollfd pfd = { fd, POLLOUT, 0 };
            if (poll(&pfd, 1, 1000) <= 0)
                return false;
            continue;
        }
        return false;
    }
    return true;
}

static bool read_exact(int fd, uint8_t *buf, size_t len, int64_t deadline)
{
    size_t off = 0;
    while (off < len) {
        int64_t left = deadline - now_ms();
        if (left <= 0)
            return false;

        struct pollfd pfd = { fd, POLLIN, 0 };
        int pr = poll(&pfd, 1, (int)left);
        if (pr == 0)
            return false;
        if (pr < 0) {
            if (errno == EINTR)
                continue;
            return false;
        }

        ssize_t n = read(fd, buf + off, len - off);
        if (n > 0) {
            off += (size_t)n;
            continue;
        }
        if (n < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
            continue;
        return false;   /* n == 0 — брокер закрив з'єднання */
    }
    return true;
}

/* Довжина решти пакета — змінне ціле по 7 біт на байт, старший біт = «є ще». */
static size_t encode_remaining(uint8_t *out, size_t len)
{
    size_t i = 0;
    do {
        uint8_t byte = (uint8_t)(len % 128);
        len /= 128;
        if (len > 0)
            byte |= 0x80;
        out[i++] = byte;
    } while (len > 0);
    return i;
}

/* Читає один пакет цілком. false — канал зламався або нічого не прийшло вчасно. */
static bool read_packet(mqtt_client_t *c, uint8_t *type, uint8_t *buf,
                        size_t cap, size_t *len, int64_t deadline)
{
    uint8_t header;
    if (!read_exact(c->fd, &header, 1, deadline))
        return false;
    *type = (uint8_t)(header & 0xF0);

    size_t remaining = 0, multiplier = 1;
    for (int i = 0; i < 4; i++) {
        uint8_t byte;
        if (!read_exact(c->fd, &byte, 1, deadline))
            return false;
        remaining += (size_t)(byte & 0x7F) * multiplier;
        if ((byte & 0x80) == 0)
            break;
        multiplier *= 128;
        if (i == 3)
            return false;   /* довжина понад чотири байти — потік зіпсовано */
    }

    if (remaining > cap)
        return false;
    if (remaining > 0 && !read_exact(c->fd, buf, remaining, deadline))
        return false;
    *len = remaining;
    return true;
}

static int tcp_connect(const char *host, const char *port, int timeout_ms)
{
    struct addrinfo hints, *res = NULL, *ai;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, port, &hints, &res) != 0)
        return -1;

    int fd = -1;
    for (ai = res; ai != NULL; ai = ai->ai_next) {
        fd = socket(ai->ai_family, ai->ai_socktype | SOCK_NONBLOCK, ai->ai_protocol);
        if (fd < 0)
            continue;
        if (connect(fd, ai->ai_addr, ai->ai_addrlen) == 0)
            break;
        if (errno == EINPROGRESS) {
            struct pollfd pfd = { fd, POLLOUT, 0 };
            if (poll(&pfd, 1, timeout_ms) == 1) {
                int err = 0;
                socklen_t elen = sizeof(err);
                if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &elen) == 0 && err == 0)
                    break;
            }
        }
        close(fd);
        fd = -1;
    }
    freeaddrinfo(res);
    if (fd < 0)
        return -1;

    /* Телеметрія — короткі пакети; затримка Nagle тут лише псує реакцію. */
    int one = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    return fd;
}

mqtt_client_t *mqtt_connect(const char *host, const char *port,
                            const char *client_id, uint16_t keepalive_s)
{
    size_t id_len = strlen(client_id);
    if (id_len == 0 || id_len > 200)
        return NULL;

    int fd = tcp_connect(host, port, CONNECT_TIMEOUT_MS);
    if (fd < 0)
        return NULL;

    uint8_t body[256];
    size_t n = 0;
    body[n++] = 0x00;                       /* довжина назви протоколу */
    body[n++] = 0x04;
    memcpy(&body[n], "MQTT", 4);
    n += 4;
    body[n++] = 0x04;                       /* рівень протоколу 4 = MQTT 3.1.1 */
    body[n++] = 0x02;                       /* clean session: черга живе у нас, не в брокері */
    body[n++] = (uint8_t)(keepalive_s >> 8);
    body[n++] = (uint8_t)(keepalive_s & 0xFF);
    body[n++] = (uint8_t)(id_len >> 8);
    body[n++] = (uint8_t)(id_len & 0xFF);
    memcpy(&body[n], client_id, id_len);
    n += id_len;

    uint8_t pkt[300];
    size_t p = 0;
    pkt[p++] = MQTT_CONNECT;
    p += encode_remaining(&pkt[p], n);
    memcpy(&pkt[p], body, n);
    p += n;

    mqtt_client_t *c = calloc(1, sizeof(*c));
    if (!c) {
        close(fd);
        return NULL;
    }
    c->fd = fd;
    c->next_pid = 1;
    c->keepalive_s = keepalive_s;

    if (!write_all(fd, pkt, p)) {
        close(fd);
        free(c);
        return NULL;
    }
    c->last_tx_ms = now_ms();

    uint8_t type = 0, buf[MQTT_MAX_PACKET];
    size_t len = 0;
    if (!read_packet(c, &type, buf, sizeof(buf), &len, now_ms() + ACK_TIMEOUT_MS) ||
        type != MQTT_CONNACK || len < 2 || buf[1] != 0x00) {
        /* buf[1] — код відмови: 0x04 хибні дані входу, 0x05 не авторизовано. */
        close(fd);
        free(c);
        return NULL;
    }
    return c;
}

void mqtt_disconnect(mqtt_client_t *c)
{
    if (!c)
        return;
    uint8_t pkt[2] = { MQTT_DISCONNECT, 0x00 };
    write_all(c->fd, pkt, sizeof(pkt));
    close(c->fd);
    free(c);
}

int mqtt_publish_qos1(mqtt_client_t *c, const char *topic, const char *payload)
{
    size_t topic_len = strlen(topic);
    size_t payload_len = strlen(payload);
    size_t remaining = 2 + topic_len + 2 + payload_len;
    if (remaining + 5 > MQTT_MAX_PACKET)
        return -1;

    uint16_t pid = c->next_pid++;
    if (c->next_pid == 0)
        c->next_pid = 1;                    /* нуль як ідентифікатор заборонено */

    uint8_t pkt[MQTT_MAX_PACKET];
    size_t p = 0;
    pkt[p++] = MQTT_PUBLISH | 0x02;         /* QoS 1, без DUP і RETAIN */
    p += encode_remaining(&pkt[p], remaining);
    pkt[p++] = (uint8_t)(topic_len >> 8);
    pkt[p++] = (uint8_t)(topic_len & 0xFF);
    memcpy(&pkt[p], topic, topic_len);
    p += topic_len;
    pkt[p++] = (uint8_t)(pid >> 8);
    pkt[p++] = (uint8_t)(pid & 0xFF);
    memcpy(&pkt[p], payload, payload_len);
    p += payload_len;

    if (!write_all(c->fd, pkt, p))
        return -1;
    c->last_tx_ms = now_ms();

    /* Чекаємо саме на PUBACK нашого пакета. Усе, що прилетить попереду
     * (наприклад, відповідь на попередній PINGREQ), просто вичитуємо. */
    int64_t deadline = now_ms() + ACK_TIMEOUT_MS;
    for (;;) {
        uint8_t type = 0, buf[MQTT_MAX_PACKET];
        size_t len = 0;
        if (!read_packet(c, &type, buf, sizeof(buf), &len, deadline))
            return -1;
        if (type == MQTT_PINGRESP) {
            c->awaiting_pingresp = false;
            continue;
        }
        if (type == MQTT_PUBACK && len >= 2) {
            uint16_t acked = (uint16_t)(((uint16_t)buf[0] << 8) | buf[1]);
            if (acked == pid)
                return 0;
        }
        /* Чужі пакети мовчки ковтаємо: ми ні на що не підписані. */
    }
}

int mqtt_keepalive(mqtt_client_t *c)
{
    int64_t now = now_ms();

    if (c->awaiting_pingresp && now > c->ping_deadline_ms)
        return -1;   /* мовчання брокера — єдина ознака мертвого каналу, яку ми маємо */

    if (!c->awaiting_pingresp && now - c->last_tx_ms >= (int64_t)c->keepalive_s * 500) {
        uint8_t pkt[2] = { MQTT_PINGREQ, 0x00 };
        if (!write_all(c->fd, pkt, sizeof(pkt)))
            return -1;
        c->last_tx_ms = now;
        c->awaiting_pingresp = true;
        c->ping_deadline_ms = now + ACK_TIMEOUT_MS;
    }

    /* Вичитуємо те, що вже лежить у сокеті, не блокуючись. */
    for (;;) {
        struct pollfd pfd = { c->fd, POLLIN, 0 };
        int pr = poll(&pfd, 1, 0);
        if (pr <= 0)
            return (pr < 0 && errno != EINTR) ? -1 : 0;

        uint8_t type = 0, buf[MQTT_MAX_PACKET];
        size_t len = 0;
        if (!read_packet(c, &type, buf, sizeof(buf), &len, now_ms() + 1000))
            return -1;
        if (type == MQTT_PINGRESP)
            c->awaiting_pingresp = false;
    }
}

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define MAX_PAYLOAD_SIZE (1024 * 1024) /* 1 МБ максимальний розмір пакета */
#define INITIAL_BUF_CAP  4096

typedef enum {
    IO_OK = 0,
    IO_WANT_READ,
    IO_WANT_WRITE,
    IO_PEER_CLOSED,
    IO_ERROR
} io_status_t;

typedef enum {
    STATE_READ_HEADER = 0,
    STATE_READ_PAYLOAD,
    STATE_FRAME_READY
} parser_state_t;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t size;
    size_t offset;
} dynamic_buffer_t;

typedef struct {
    int fd;
    parser_state_t rx_state;
    uint32_t expected_payload_len;
    dynamic_buffer_t rx_buf;
    dynamic_buffer_t tx_buf;
} nonblocking_conn_t;

static bool buf_init(dynamic_buffer_t *b, size_t cap) {
    b->data = (uint8_t *)malloc(cap);
    if (!b->data) return false;
    b->capacity = cap;
    b->size = 0;
    b->offset = 0;
    return true;
}

static void buf_free(dynamic_buffer_t *b) {
    if (b->data) {
        free(b->data);
        b->data = NULL;
    }
    b->capacity = b->size = b->offset = 0;
}

static bool buf_ensure_capacity(dynamic_buffer_t *b, size_t needed) {
    if (b->capacity >= needed) return true;
    size_t new_cap = b->capacity * 2;
    if (new_cap < needed) new_cap = needed;
    uint8_t *tmp = (uint8_t *)realloc(b->data, new_cap);
    if (!tmp) return false;
    b->data = tmp;
    b->capacity = new_cap;
    return true;
}

/* Компактифікація буфера: перенесення необробленого залишку на початок */
static void buf_compact(dynamic_buffer_t *b) {
    if (b->offset == 0) return;
    if (b->offset >= b->size) {
        b->size = 0;
        b->offset = 0;
    } else {
        size_t remaining = b->size - b->offset;
        memmove(b->data, b->data + b->offset, remaining);
        b->size = remaining;
        b->offset = 0;
    }
}

int set_socket_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

nonblocking_conn_t* conn_create(int fd) {
    if (set_socket_nonblocking(fd) < 0) return NULL;
    nonblocking_conn_t *c = (nonblocking_conn_t *)calloc(1, sizeof(nonblocking_conn_t));
    if (!c) return NULL;
    c->fd = fd;
    c->rx_state = STATE_READ_HEADER;
    if (!buf_init(&c->rx_buf, INITIAL_BUF_CAP) || !buf_init(&c->tx_buf, INITIAL_BUF_CAP)) {
        buf_free(&c->rx_buf);
        buf_free(&c->tx_buf);
        free(c);
        return NULL;
    }
    return c;
}

void conn_destroy(nonblocking_conn_t *c) {
    if (!c) return;
    if (c->fd >= 0) close(c->fd);
    buf_free(&c->rx_buf);
    buf_free(&c->tx_buf);
    free(c);
}

/* Неблокуюче читання до вичерпання буфера ядра (до отримання EAGAIN) */
io_status_t conn_read_nonblocking(nonblocking_conn_t *c) {
    while (true) {
        buf_compact(&c->rx_buf);
        if (!buf_ensure_capacity(&c->rx_buf, c->rx_buf.size + 4096)) {
            return IO_ERROR;
        }

        ssize_t n = read(c->fd, c->rx_buf.data + c->rx_buf.size, 4096);
        if (n > 0) {
            c->rx_buf.size += (size_t)n;
            continue; /* Вичитуємо всі доступні байти в буфері */
        }
        if (n == 0) {
            return IO_PEER_CLOSED; /* Віддалена сторона надіслала TCP FIN */
        }
        if (errno == EINTR) {
            continue; /* Системний сигнал — повторюємо виклик */
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return IO_WANT_READ; /* Буфер порожній — повертаємося до мультиплексора */
        }
        return IO_ERROR;
    }
}

/* Розбір накопичених кадрів автоматом */
bool conn_parse_frames(nonblocking_conn_t *c, void (*on_frame)(const uint8_t *payload, size_t len)) {
    while (true) {
        size_t available = c->rx_buf.size - c->rx_buf.offset;

        if (c->rx_state == STATE_READ_HEADER) {
            if (available < sizeof(uint32_t)) {
                return true; /* Недостатньо байтів для читання довжини */
            }
            uint32_t net_len = 0;
            memcpy(&net_len, c->rx_buf.data + c->rx_buf.offset, sizeof(uint32_t));
            c->expected_payload_len = ntohl(net_len);
            c->rx_buf.offset += sizeof(uint32_t);

            if (c->expected_payload_len > MAX_PAYLOAD_SIZE) {
                return false; /* Захист від некоректного розміру кадру */
            }
            c->rx_state = STATE_READ_PAYLOAD;
            available = c->rx_buf.size - c->rx_buf.offset;
        }

        if (c->rx_state == STATE_READ_PAYLOAD) {
            if (available < c->expected_payload_len) {
                return true; /* Тіло кадру надійшло не повністю */
            }
            const uint8_t *payload_ptr = c->rx_buf.data + c->rx_buf.offset;
            on_frame(payload_ptr, c->expected_payload_len);
            c->rx_buf.offset += c->expected_payload_len;

            /* Повертаємося до пошуку наступного кадру */
            c->rx_state = STATE_READ_HEADER;
            c->expected_payload_len = 0;
        }
    }
}

/* Додавання повідомлення у вихідну чергу */
bool conn_enqueue_message(nonblocking_conn_t *c, const uint8_t *payload, size_t len) {
    if (len > MAX_PAYLOAD_SIZE) return false;
    buf_compact(&c->tx_buf);

    size_t total_frame_len = sizeof(uint32_t) + len;
    if (!buf_ensure_capacity(&c->tx_buf, c->tx_buf.size + total_frame_len)) {
        return false;
    }

    uint32_t net_len = htonl((uint32_t)len);
    memcpy(c->tx_buf.data + c->tx_buf.size, &net_len, sizeof(uint32_t));
    c->tx_buf.size += sizeof(uint32_t);

    memcpy(c->tx_buf.data + c->tx_buf.size, payload, len);
    c->tx_buf.size += len;
    return true;
}

/* Скидання вихідного буфера в сокет */
io_status_t conn_flush_write(nonblocking_conn_t *c) {
    while (c->tx_buf.offset < c->tx_buf.size) {
        size_t to_write = c->tx_buf.size - c->tx_buf.offset;
        ssize_t n = write(c->fd, c->tx_buf.data + c->tx_buf.offset, to_write);

        if (n > 0) {
            c->tx_buf.offset += (size_t)n;
            continue;
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return IO_WANT_WRITE; /* Буфер ядра заповнений — чекаємо готовності на запис */
        }
        return IO_ERROR;
    }

    buf_compact(&c->tx_buf);
    return IO_OK;
}

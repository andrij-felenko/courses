/* ============================================================================
 * Високопродуктивний міст MAVLink між MCU та Companion (C99 / Linux)
 * ============================================================================ */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <time.h>
#include <sys/epoll.h>
#include <sched.h>

#define MAVLINK_STX_V2          0xFD
#define MAX_PACKET_LEN          280
#define RING_BUF_SIZE           8192

/* Структура кільцевого буфера без блокувань для одного потоку запису і читання */
typedef struct {
    uint8_t buffer[RING_BUF_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} ring_buffer_t;

static inline bool ring_buf_push(ring_buffer_t *rb, uint8_t byte) {
    uint32_t next_head = (rb->head + 1) & (RING_BUF_SIZE - 1);
    if (next_head == rb->tail) {
        return false; /* Переповнення буфера */
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head;
    return true;
}

static inline bool ring_buf_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; /* Буфер порожній */
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & (RING_BUF_SIZE - 1);
    return true;
}

/* Стан парсера пакетів MAVLink v2 */
typedef enum {
    STATE_UNSYNC = 0,
    STATE_GOT_STX,
    STATE_GOT_LEN,
    STATE_GOT_INCOMPAT,
    STATE_GOT_COMPAT,
    STATE_GOT_SEQ,
    STATE_GOT_SYSID,
    STATE_GOT_COMPID,
    STATE_GOT_MSGID_0,
    STATE_GOT_MSGID_1,
    STATE_GOT_MSGID_2,
    STATE_PAYLOAD,
    STATE_CRC
} parse_state_t;

typedef struct {
    uint8_t length;
    uint8_t incompat_flags;
    uint8_t compat_flags;
    uint8_t seq;
    uint8_t sysid;
    uint8_t compid;
    uint32_t msgid;
    uint8_t payload[255];
    uint16_t checksum;
    uint8_t payload_idx;
    uint8_t crc_idx;
} mavlink_rx_msg_t;

typedef struct {
    int uart_fd;
    int epoll_fd;
    ring_buffer_t rx_ring;
    parse_state_t state;
    mavlink_rx_msg_t current_msg;
    uint64_t last_valid_rx_ms;
    uint32_t packets_received;
    uint32_t crc_errors;
} companion_bridge_t;

/* Отримання поточного монотонного часу */
static uint64_t get_now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Ініціалізація та підвищення пріоритету потоку до SCHED_FIFO */
int companion_bridge_init(companion_bridge_t *br, const char *dev, speed_t baud) {
    memset(br, 0, sizeof(*br));

    br->uart_fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (br->uart_fd < 0) {
        perror("Не вдалося відкрити порт UART");
        return -1;
    }

    struct termios tty;
    if (tcgetattr(br->uart_fd, &tty) < 0) {
        close(br->uart_fd);
        return -1;
    }

    cfmakeraw(&tty);
    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);

    tty.c_cflag |= (CLOCAL | CREAD | CS8);
    tty.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(br->uart_fd, TCSANOW, &tty) < 0) {
        close(br->uart_fd);
        return -1;
    }

    /* Налаштування epoll для енергоефективного очікування даних */
    br->epoll_fd = epoll_create1(0);
    if (br->epoll_fd < 0) {
        close(br->uart_fd);
        return -1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = br->uart_fd;
    if (epoll_ctl(br->epoll_fd, EPOLL_CTL_ADD, br->uart_fd, &ev) < 0) {
        close(br->epoll_fd);
        close(br->uart_fd);
        return -1;
    }

    /* Спроба встановити пріоритет реального часу SCHED_FIFO */
    struct sched_param sp;
    sp.sched_priority = 80;
    sched_setscheduler(0, SCHED_FIFO, &sp);

    br->last_valid_rx_ms = get_now_ms();
    return 0;
}

/* Обробка надходження сирих байтів у кільцевий буфер */
int companion_bridge_read_fd(companion_bridge_t *br) {
    uint8_t chunk[512];
    ssize_t n = read(br->uart_fd, chunk, sizeof(chunk));
    if (n > 0) {
        for (ssize_t i = 0; i < n; ++i) {
            ring_buf_push(&br->rx_ring, chunk[i]);
        }
        return (int)n;
    }
    return (n < 0 && errno == EAGAIN) ? 0 : -1;
}

/* Кінцевий автомат розбору потоку байтів MAVLink v2 */
bool companion_bridge_parse_next(companion_bridge_t *br, mavlink_rx_msg_t *out_msg) {
    uint8_t b;
    while (ring_buf_pop(&br->rx_ring, &b)) {
        switch (br->state) {
            case STATE_UNSYNC:
                if (b == MAVLINK_STX_V2) br->state = STATE_GOT_STX;
                break;
            case STATE_GOT_STX:
                br->current_msg.length = b;
                br->state = STATE_GOT_LEN;
                break;
            case STATE_GOT_LEN:
                br->current_msg.incompat_flags = b;
                br->state = STATE_GOT_INCOMPAT;
                break;
            case STATE_GOT_INCOMPAT:
                br->current_msg.compat_flags = b;
                br->state = STATE_GOT_COMPAT;
                break;
            case STATE_GOT_COMPAT:
                br->current_msg.seq = b;
                br->state = STATE_GOT_SEQ;
                break;
            case STATE_GOT_SEQ:
                br->current_msg.sysid = b;
                br->state = STATE_GOT_SYSID;
                break;
            case STATE_GOT_SYSID:
                br->current_msg.compid = b;
                br->state = STATE_GOT_COMPID;
                break;
            case STATE_GOT_COMPID:
                br->current_msg.msgid = b;
                br->state = STATE_GOT_MSGID_0;
                break;
            case STATE_GOT_MSGID_0:
                br->current_msg.msgid |= ((uint32_t)b << 8);
                br->state = STATE_GOT_MSGID_1;
                break;
            case STATE_GOT_MSGID_1:
                br->current_msg.msgid |= ((uint32_t)b << 16);
                br->current_msg.payload_idx = 0;
                br->state = (br->current_msg.length > 0) ? STATE_PAYLOAD : STATE_CRC;
                break;
            case STATE_PAYLOAD:
                br->current_msg.payload[br->current_msg.payload_idx++] = b;
                if (br->current_msg.payload_idx >= br->current_msg.length) {
                    br->current_msg.crc_idx = 0;
                    br->state = STATE_CRC;
                }
                break;
            case STATE_CRC:
                if (br->current_msg.crc_idx == 0) {
                    br->current_msg.checksum = b;
                    br->current_msg.crc_idx = 1;
                } else {
                    br->current_msg.checksum |= ((uint16_t)b << 8);
                    br->state = STATE_UNSYNC;
                    br->packets_received++;
                    br->last_valid_rx_ms = get_now_ms();
                    memcpy(out_msg, &br->current_msg, sizeof(mavlink_rx_msg_t));
                    return true;
                }
                break;
        }
    }
    return false;
}

/* Відправка уставки позиції у форматі SET_POSITION_TARGET_LOCAL_NED */
int companion_bridge_send_target_ned(companion_bridge_t *br, float x, float y, float z, float yaw) {
    uint8_t packet[75];
    /* Заголовок MAVLink v2 */
    packet[0] = MAVLINK_STX_V2;
    packet[1] = 53; /* Довжина корисного навантаження */
    packet[2] = 0;  /* Incompat flags */
    packet[3] = 0;  /* Compat flags */
    packet[4] = (uint8_t)(br->packets_received & 0xFF); /* Seq */
    packet[5] = 1;  /* SysID Companion */
    packet[6] = 191;/* CompID Companion (MAV_COMP_ID_ONBOARD_COMPUTER) */
    packet[7] = 84; /* MsgID 84 = SET_POSITION_TARGET_LOCAL_NED */
    packet[8] = 0;
    packet[9] = 0;

    /* Корисне навантаження: time_boot_ms (4B), target_system, target_component, coord_frame... */
    uint32_t boot_ms = (uint32_t)get_now_ms();
    memcpy(&packet[10], &boot_ms, 4);
    packet[14] = 1; /* Target System = 1 (FC) */
    packet[15] = 1; /* Target Component = 1 (Autopilot) */
    packet[16] = 1; /* MAV_FRAME_LOCAL_NED */
    uint16_t type_mask = 0b0000101111111000; /* Ігнорувати швидкість/прискорення, тримати позицію */
    memcpy(&packet[17], &type_mask, 2);
    memcpy(&packet[19], &x, 4);
    memcpy(&packet[23], &y, 4);
    memcpy(&packet[27], &z, 4);

    /* Фіктивна контрольна сума для прикладу */
    uint16_t crc = 0xABCD;
    memcpy(&packet[63], &crc, 2);

    ssize_t written = write(br->uart_fd, packet, 65);
    return (written == 65) ? 0 : -1;
}

void companion_bridge_close(companion_bridge_t *br) {
    if (br->epoll_fd >= 0) close(br->epoll_fd);
    if (br->uart_fd >= 0) close(br->uart_fd);
    br->epoll_fd = -1;
    br->uart_fd = -1;
}

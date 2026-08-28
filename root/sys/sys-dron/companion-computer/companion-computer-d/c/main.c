/* ============================================================================
 * Драйвер послідовного порту MAVLink для бортового комп'ютера (C99 / POSIX)
 * ============================================================================ */
#define _POSIX_C_SOURCE 200809L
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

/* Базові константи та типи протоколу MAVLink v2 */
#define MAVLINK_STX_V2          0xFD
#define MAVLINK_MAX_PACKET_LEN  280
#define BUFFER_SIZE             1024

typedef struct {
    int fd;
    char device[64];
    speed_t baudrate;
    uint8_t rx_buffer[BUFFER_SIZE];
    uint32_t rx_head;
    uint32_t rx_tail;
    uint64_t last_heartbeat_ms;
} serial_bridge_t;

/* Отримання поточного часу в мілісекундах */
static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Ініціалізація та конфігурація POSIX UART у режимі RAW */
int serial_bridge_open(serial_bridge_t *b, const char *device, speed_t baud) {
    memset(b, 0, sizeof(*b));
    strncpy(b->device, device, sizeof(b->device) - 1);
    b->baudrate = baud;

    /* Відкриття порту: неблокуючий режим, без захоплення терміналу */
    b->fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (b->fd < 0) {
        perror("Помилка відкриття UART");
        return -1;
    }

    struct termios config;
    if (tcgetattr(b->fd, &config) < 0) {
        perror("Помилка отримання конфігурації termios");
        close(b->fd);
        return -1;
    }

    /* Налаштування сирого режиму (RAW mode) */
    cfmakeraw(&config);
    cfsetispeed(&config, baud);
    cfsetospeed(&config, baud);

    /* 8 біт даних, 1 стоп-біт, без парності, без апаратного контролю */
    config.c_cflag |= (CLOCAL | CREAD | CS8);
    config.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);

    /* Неблокуюче читання: негайне повернення, якщо буфер порожній */
    config.c_cc[VMIN] = 0;
    config.c_cc[VTIME] = 0;

    if (tcsetattr(b->fd, TCSANOW, &config) < 0) {
        perror("Помилка застосування termios");
        close(b->fd);
        return -1;
    }

    tcflush(b->fd, TCIOFLUSH);
    b->last_heartbeat_ms = get_time_ms();
    return 0;
}

/* Неблокуюче читання та базовий парсинг STX маркера MAVLink */
int serial_bridge_poll_rx(serial_bridge_t *b) {
    uint8_t temp_buf[256];
    ssize_t bytes_read = read(b->fd, temp_buf, sizeof(temp_buf));

    if (bytes_read > 0) {
        for (ssize_t i = 0; i < bytes_read; ++i) {
            uint8_t byte = temp_buf[i];
            /* Виявлення початку кадру MAVLink v2 */
            if (byte == MAVLINK_STX_V2) {
                b->last_heartbeat_ms = get_time_ms();
            }
        }
        return (int)bytes_read;
    }
    return 0;
}

/* Відправка бінарного пакета у порт */
ssize_t serial_bridge_send(serial_bridge_t *b, const uint8_t *data, size_t len) {
    if (b->fd < 0 || !data || len == 0) return -1;
    return write(b->fd, data, len);
}

/* Перевірка таймауту зв'язку з політним контролером */
bool serial_bridge_is_alive(const serial_bridge_t *b, uint32_t timeout_ms) {
    uint64_t now = get_time_ms();
    return (now - b->last_heartbeat_ms) < (uint64_t)timeout_ms;
}

void serial_bridge_close(serial_bridge_t *b) {
    if (b->fd >= 0) {
        close(b->fd);
        b->fd = -1;
    }
}

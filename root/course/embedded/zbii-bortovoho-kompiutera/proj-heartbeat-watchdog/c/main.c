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
#include <sched.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <gpiod.h>

#define SOCKET_PATH      "/tmp/companion_health.sock"
#define SERIAL_PORT      "/dev/ttyAMA0"
#define BAUDRATE         B921600
#define GPIO_CHIP_NAME   "gpiochip0"
#define WATCHDOG_PIN     17

#define HEARTBEAT_PERIOD_MS   1000
#define STROBE_PERIOD_MS      100
#define PROCESS_TIMEOUT_SEC   2

/* Структура корисного навантаження MAVLink v2 HEARTBEAT (Message ID 0) */
#pragma pack(push, 1)
typedef struct {
    uint32_t custom_mode;
    uint8_t  type;           /* MAV_TYPE_ONBOARD_CONTROLLER = 18 */
    uint8_t  autopilot;      /* MAV_AUTOPILOT_INVALID = 8 */
    uint8_t  base_mode;      /* MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1 */
    uint8_t  system_status;  /* MAV_STATE_ACTIVE = 3, MAV_STATE_CRITICAL = 5 */
    uint8_t  mavlink_version;/* 3 для версії протоколу MAVLink v2 */
} mavlink_heartbeat_payload_t;

typedef struct {
    uint8_t  magic;          /* Стартовий байт 0xFD для MAVLink v2 */
    uint8_t  len;            /* Довжина пейлоаду (9 байтів) */
    uint8_t  incompat_flags; /* Прапорці несумісності (0) */
    uint8_t  compat_flags;   /* Прапорці сумісності (0) */
    uint8_t  seq;            /* Порядковий номер пакета */
    uint8_t  sysid;          /* Системний ID апарата (1) */
    uint8_t  compid;         /* ID компонента: MAV_COMP_ID_ONBOARD_COMPUTER = 191 */
    uint8_t  msgid[3];       /* ID повідомлення: 0 = [0x00, 0x00, 0x00] */
    mavlink_heartbeat_payload_t payload;
    uint16_t checksum;       /* Контрольна сума CRC-16-CCITT + CRC_EXTRA (50) */
} mavlink_v2_heartbeat_packet_t;
#pragma pack(pop)

/* Накопичувальний розрахунок контрольної суми MAVLink X.25 */
static uint16_t crc_accumulate(uint8_t byte, uint16_t crc) {
    uint8_t ch = byte ^ (uint8_t)(crc & 0x00FF);
    ch = (uint8_t)(ch ^ (ch << 4));
    return (uint16_t)((crc >> 8) ^ ((uint16_t)ch << 8) ^ ((uint16_t)ch << 3) ^ ((uint16_t)ch >> 4));
}

static uint16_t calculate_mavlink_crc(const uint8_t *buffer, size_t len, uint8_t crc_extra) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 1; i < len; ++i) { /* Пропуск стартового байта 0xFD */
        crc = crc_accumulate(buffer[i], crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}

static int configure_realtime_priority(void) {
    struct sched_param param;
    param.sched_priority = 50;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("Попередження: не вдалося встановити SCHED_FIFO");
    }
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("Попередження: не вдалося заблокувати пам'ять mlockall");
    }
    return 0;
}

static int open_serial_port(const char *dev, speed_t speed) {
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        perror("Помилка відкриття послідовного порту");
        return -1;
    }
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }
    cfmakeraw(&tty);
    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS;
    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static int setup_unix_server_socket(const char *path) {
    unlink(path);
    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK, 0);
    if (fd < 0) {
        perror("Помилка створення UNIX сокета");
        return -1;
    }
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка прив'язки UNIX сокета");
        close(fd);
        return -1;
    }
    chmod(path, 0666);
    return fd;
}

int main(void) {
    configure_realtime_priority();

    int serial_fd = open_serial_port(SERIAL_PORT, BAUDRATE);
    int sock_fd = setup_unix_server_socket(SOCKET_PATH);
    if (serial_fd < 0 || sock_fd < 0) {
        return EXIT_FAILURE;
    }

    struct gpiod_chip *chip = gpiod_chip_open_by_name(GPIO_CHIP_NAME);
    struct gpiod_line *line = NULL;
    if (chip) {
        line = gpiod_chip_get_line(chip, WATCHDOG_PIN);
        if (line) {
            gpiod_line_request_output(line, "companion-watchdog", 0);
        }
    }

    uint8_t packet_seq = 0;
    int pin_state = 0;
    time_t last_worker_ping = time(NULL);
    struct timespec last_hb_time, last_strobe_time, now;
    clock_gettime(CLOCK_MONOTONIC, &last_hb_time);
    clock_gettime(CLOCK_MONOTONIC, &last_strobe_time);

    printf("Companion Watchdog запущено. Моніторинг сокета: %s\n", SOCKET_PATH);

    while (1) {
        clock_gettime(CLOCK_MONOTONIC, &now);

        /* 1. Опитування черги повідомлень від робочих процесів */
        char buf[32];
        ssize_t bytes = recv(sock_fd, buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            if (strncmp(buf, "ALIVE", 5) == 0) {
                last_worker_ping = time(NULL);
            }
        }

        bool worker_healthy = (time(NULL) - last_worker_ping) < PROCESS_TIMEOUT_SEC;

        /* 2. Апаратне стробування GPIO виводу */
        int64_t strobe_dt_ms = (now.tv_sec - last_strobe_time.tv_sec) * 1000 +
                               (now.tv_nsec - last_strobe_time.tv_nsec) / 1000000;
        if (strobe_dt_ms >= STROBE_PERIOD_MS) {
            if (worker_healthy && line) {
                pin_state = !pin_state;
                gpiod_line_set_value(line, pin_state);
            } else if (line) {
                gpiod_line_set_value(line, 0); /* Скидання стробу при аварії */
            }
            last_strobe_time = now;
        }

        /* 3. Генерація кадру MAVLink HEARTBEAT */
        int64_t hb_dt_ms = (now.tv_sec - last_hb_time.tv_sec) * 1000 +
                           (now.tv_nsec - last_hb_time.tv_nsec) / 1000000;
        if (hb_dt_ms >= HEARTBEAT_PERIOD_MS) {
            mavlink_v2_heartbeat_packet_t pkt;
            memset(&pkt, 0, sizeof(pkt));

            pkt.magic = 0xFD;
            pkt.len = sizeof(mavlink_heartbeat_payload_t);
            pkt.incompat_flags = 0;
            pkt.compat_flags = 0;
            pkt.seq = packet_seq++;
            pkt.sysid = 1;
            pkt.compid = 191; /* MAV_COMP_ID_ONBOARD_COMPUTER */
            pkt.msgid[0] = 0x00;
            pkt.msgid[1] = 0x00;
            pkt.msgid[2] = 0x00;

            pkt.payload.type = 18; /* MAV_TYPE_ONBOARD_CONTROLLER */
            pkt.payload.autopilot = 8; /* MAV_AUTOPILOT_INVALID */
            pkt.payload.base_mode = 1; /* MAV_MODE_FLAG_CUSTOM_MODE_ENABLED */
            pkt.payload.system_status = worker_healthy ? 3 : 5; /* 3=ACTIVE, 5=CRITICAL */
            pkt.payload.mavlink_version = 3;

            size_t payload_and_header_len = 10 + sizeof(mavlink_heartbeat_payload_t);
            pkt.checksum = calculate_mavlink_crc((const uint8_t *)&pkt, payload_and_header_len, 50);

            if (write(serial_fd, &pkt, sizeof(pkt)) < 0) {
                perror("Помилка відправки HEARTBEAT");
            }
            last_hb_time = now;
        }

        usleep(10000); /* Крок опитування 10 мс */
    }

    if (line) gpiod_line_release(line);
    if (chip) gpiod_chip_close(chip);
    close(sock_fd);
    close(serial_fd);
    unlink(SOCKET_PATH);
    return EXIT_SUCCESS;
}

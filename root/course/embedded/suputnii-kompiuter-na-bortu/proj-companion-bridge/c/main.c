#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <linux/serial.h>
#include <mavlink.h>

#define SERIAL_PORT "/dev/ttyAMA0"
#define SYSTEM_ID   1
#define COMPONENT_ID MAV_COMP_ID_ONBOARD_COMPUTER

typedef struct {
    int fd;
    volatile bool running;
    pthread_t rx_thread;
    pthread_t hb_thread;
    pthread_t tx_thread;
    float current_yaw;
} companion_bridge_t;

static int configure_serial(int fd) {
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) return -1;

    // 921600 бод, 8N1, апаратний flow control CTS/RTS
    cfsetospeed(&tty, B921600);
    cfsetispeed(&tty, B921600);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD | CRTSCTS);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB);

    // Сирий (raw) режим без перетворень байтів
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF | IXANY);
    tty.c_oflag &= ~(OPOST | ONLCR);
    tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 1; // таймаут 100 мс

    if (tcsetattr(fd, TCSANOW, &tty) != 0) return -1;

    // Зниження затримки ядра Linux
    struct serial_struct ser_info;
    if (ioctl(fd, TIOCGSERIAL, &ser_info) == 0) {
        ser_info.flags |= ASYNC_LOW_LATENCY;
        ioctl(fd, TIOCSSERIAL, &ser_info);
    }
    return 0;
}

static void* rx_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[512];
    mavlink_message_t msg;
    mavlink_status_t status;

    while (b->running) {
        ssize_t n = read(b->fd, buf, sizeof(buf));
        if (n > 0) {
            for (ssize_t i = 0; i < n; ++i) {
                if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)) {
                    if (msg.msgid == MAVLINK_MSG_ID_ATTITUDE) {
                        mavlink_attitude_t att;
                        mavlink_msg_attitude_decode(&msg, &att);
                        b->current_yaw = att.yaw;
                    }
                }
            }
        }
    }
    return NULL;
}

static void* hb_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_message_t msg;

    while (b->running) {
        mavlink_msg_heartbeat_pack(SYSTEM_ID, COMPONENT_ID, &msg,
                                   MAV_TYPE_ONBOARD_CONTROLLER,
                                   MAV_AUTOPILOT_INVALID,
                                   MAV_MODE_FLAG_SAFETY_ARMED,
                                   0, MAV_STATE_ACTIVE);
        uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
        write(b->fd, buf, len);
        sleep(1);
    }
    return NULL;
}

static void* tx_worker(void* arg) {
    companion_bridge_t* b = (companion_bridge_t*)arg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_message_t msg;

    // Маска керування вектором швидкості (Vx=1.0 м/с вперед, Vy=0, Vz=0)
    // Ігнорувати позицію та прискорення: (1<<0)|(1<<1)|(1<<2)|(1<<6)|(1<<7)|(1<<8) = 0x01C7
    uint16_t type_mask = 0x01C7;

    while (b->running) {
        mavlink_msg_set_position_target_local_ned_pack(
            SYSTEM_ID, COMPONENT_ID, &msg,
            0, 1, 1, MAV_FRAME_LOCAL_NED,
            type_mask,
            0.0f, 0.0f, 0.0f,       // X, Y, Z (ігноруються)
            1.0f, 0.0f, 0.0f,       // Vx = 1.0 м/с, Vy = 0, Vz = 0
            0.0f, 0.0f, 0.0f,       // Ax, Ay, Az (ігноруються)
            0.0f, 0.0f              // Yaw, Yaw_Rate
        );
        uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
        write(b->fd, buf, len);
        usleep(50000); // 20 Гц (50 мс)
    }
    return NULL;
}

int main(void) {
    int fd = open(SERIAL_PORT, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        perror("Не вдалося відкрити послідовний порт");
        return 1;
    }

    if (configure_serial(fd) != 0) {
        perror("Помилка конфігурації termios");
        close(fd);
        return 1;
    }

    companion_bridge_t bridge = {.fd = fd, .running = true, .current_yaw = 0.0f};

    pthread_create(&bridge.rx_thread, NULL, rx_worker, &bridge);
    pthread_create(&bridge.hb_thread, NULL, hb_worker, &bridge);
    pthread_create(&bridge.tx_thread, NULL, tx_worker, &bridge);

    printf("Companion Bridge запущено. Натисніть Enter для зупинки...\n");
    getchar();

    bridge.running = false;
    pthread_join(bridge.rx_thread, NULL);
    pthread_join(bridge.hb_thread, NULL);
    pthread_join(bridge.tx_thread, NULL);

    close(fd);
    printf("Companion Bridge коректно зупинено.\n");
    return 0;
}

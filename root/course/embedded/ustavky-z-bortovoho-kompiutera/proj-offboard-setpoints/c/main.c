#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <pthread.h>
#include <sys/timerfd.h>
#include <sys/time.h>
#include <math.h>
#include <common/mavlink.h>

#define UART_PORT "/dev/ttyAMA0"
#define UART_BAUDRATE B921600
#define STREAM_FREQ_HZ 20
#define PRESTREAM_FRAMES 16
#define PLANNER_TIMEOUT_MS 250

typedef enum {
    STREAMER_IDLE,
    STREAMER_PRESTREAM,
    STREAMER_REQUEST_MODE,
    STREAMER_ACTIVE,
    STREAMER_HOLD
} streamer_state_t;

typedef struct {
    pthread_mutex_t lock;
    float vx;
    float vy;
    float vz;
    float yaw;
    uint64_t last_update_ms;
    bool valid;
} shared_target_t;

typedef struct {
    int uart_fd;
    int timer_fd;
    streamer_state_t state;
    uint32_t prestream_count;
    uint8_t sys_id;
    uint8_t comp_id;
    shared_target_t target;
    bool running;
} offboard_streamer_t;

static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

static int open_uart(const char *port, speed_t baud) {
    int fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return -1;

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfmakeraw(&tty);
    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS; /* Без апаратного керування лініями flow control */

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static void send_setpoint(int fd, uint8_t sys_id, uint8_t comp_id,
                          float vx, float vy, float vz, float yaw) {
    mavlink_set_position_target_local_ned_t sp = {0};
    sp.time_boot_ms = 0;
    sp.target_system = 1;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;

    /* Маска швидкостей: ігноруємо координати, прискорення та швидкість yaw */
    sp.type_mask = 0x0001 | 0x0002 | 0x0004 | 0x0040 | 0x0080 | 0x0100 | 0x0800;
    sp.vx = vx;
    sp.vy = vy;
    sp.vz = vz;
    sp.yaw = yaw;

    mavlink_message_t msg;
    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, &msg, &sp);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

static void request_offboard_mode(int fd, uint8_t sys_id, uint8_t comp_id) {
    mavlink_command_long_t cmd = {0};
    cmd.target_system = 1;
    cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
    cmd.command = MAV_CMD_DO_SET_MODE;
    cmd.param1 = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
    cmd.param2 = 6.0f; /* PX4_CUSTOM_MAIN_MODE_OFFBOARD */

    mavlink_message_t msg;
    mavlink_msg_command_long_encode(sys_id, comp_id, &msg, &cmd);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

void* streamer_thread_func(void *arg) {
    offboard_streamer_t *ctx = (offboard_streamer_t*)arg;

    /* Налаштування періодичного таймера timerfd */
    struct itimerspec period;
    period.it_interval.tv_sec = 0;
    period.it_interval.tv_nsec = 1000000000L / STREAM_FREQ_HZ;
    period.it_value = period.it_interval;

    timerfd_settime(ctx->timer_fd, 0, &period, NULL);

    while (ctx->running) {
        uint64_t expirations = 0;
        ssize_t s = read(ctx->timer_fd, &expirations, sizeof(expirations));
        if (s <= 0) continue;

        uint64_t now = get_time_ms();
        float cur_vx = 0.0f, cur_vy = 0.0f, cur_vz = 0.0f, cur_yaw = 0.0f;
        bool is_fresh = false;

        pthread_mutex_lock(&ctx->target.lock);
        if (ctx->target.valid && (now - ctx->target.last_update_ms <= PLANNER_TIMEOUT_MS)) {
            cur_vx = ctx->target.vx;
            cur_vy = ctx->target.vy;
            cur_vz = ctx->target.vz;
            cur_yaw = ctx->target.yaw;
            is_fresh = true;
        }
        pthread_mutex_unlock(&ctx->target.lock);

        switch (ctx->state) {
        case STREAMER_IDLE:
            break;

        case STREAMER_PRESTREAM:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            ctx->prestream_count++;
            if (ctx->prestream_count >= PRESTREAM_FRAMES) {
                ctx->state = STREAMER_REQUEST_MODE;
            }
            break;

        case STREAMER_REQUEST_MODE:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            request_offboard_mode(ctx->uart_fd, ctx->sys_id, ctx->comp_id);
            ctx->state = STREAMER_ACTIVE;
            break;

        case STREAMER_ACTIVE:
            if (!is_fresh) {
                ctx->state = STREAMER_HOLD;
                send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            } else {
                send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, cur_vx, cur_vy, cur_vz, cur_yaw);
            }
            break;

        case STREAMER_HOLD:
            send_setpoint(ctx->uart_fd, ctx->sys_id, ctx->comp_id, 0.0f, 0.0f, 0.0f, cur_yaw);
            if (is_fresh) {
                ctx->state = STREAMER_ACTIVE;
            }
            break;
        }
    }
    return NULL;
}

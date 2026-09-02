#define _GNU_SOURCE

#include "mavlink_link.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

/* Збірка: -I<mavlink>/v2.0 — каталог, згенерований mavgenerate. */
#include <common/mavlink.h>

static speed_t baud_to_speed(int baud)
{
    switch (baud) {
    case 57600:   return B57600;
    case 115200:  return B115200;
    case 230400:  return B230400;
    case 460800:  return B460800;
    case 921600:  return B921600;
    default:      return 0;
    }
}

int mavlink_link_open(MavlinkLink *link, const char *device, int baud)
{
    memset(link, 0, sizeof(*link));
    link->fd = -1;
    link->sysid = 1;
    link->compid = MAV_COMP_ID_ONBOARD_COMPUTER;
    link->target_sysid = 1;
    link->target_compid = MAV_COMP_ID_AUTOPILOT1;

    const speed_t speed = baud_to_speed(baud);
    if (speed == 0) {
        fprintf(stderr, "mavlink: непідтримувана швидкість %d\n", baud);
        return -1;
    }

    /* O_NONBLOCK: контур керування не має права зупинитися на read(). */
    const int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK | O_CLOEXEC);
    if (fd < 0) {
        perror("mavlink: open");
        return -1;
    }

    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) {
        perror("mavlink: tcgetattr");
        close(fd);
        return -1;
    }

    cfmakeraw(&tio);
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= (tcflag_t)~CRTSCTS;
    tio.c_cc[VMIN] = 0;
    tio.c_cc[VTIME] = 0;
    if (cfsetispeed(&tio, speed) != 0 || cfsetospeed(&tio, speed) != 0 ||
        tcsetattr(fd, TCSANOW, &tio) != 0) {
        perror("mavlink: tcsetattr");
        close(fd);
        return -1;
    }
    tcflush(fd, TCIOFLUSH);

    link->fd = fd;
    return 0;
}

void mavlink_link_close(MavlinkLink *link)
{
    if (link->fd >= 0) {
        close(link->fd);
        link->fd = -1;
    }
}

int mavlink_link_poll(MavlinkLink *link)
{
    if (link->fd < 0) {
        return -1;
    }

    static mavlink_message_t msg;
    static mavlink_status_t status;

    uint8_t buf[512];
    int updates = 0;

    for (;;) {
        const ssize_t n = read(link->fd, buf, sizeof(buf));
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break;      /* байтів більше немає — це норма */
            }
            perror("mavlink: read");
            return -1;
        }
        if (n == 0) {
            break;
        }

        for (ssize_t i = 0; i < n; ++i) {
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) != 1) {
                continue;
            }
            if (msg.msgid != MAVLINK_MSG_ID_HIGHRES_IMU) {
                continue;
            }
            mavlink_highres_imu_t imu;
            mavlink_msg_highres_imu_decode(&msg, &imu);
            /* Рамка тіла FRD: xgyro — крен, ygyro — тангаж, zgyro — рискання. */
            link->gyro_pitch = imu.ygyro;
            link->gyro_yaw = imu.zgyro;
            link->gyro_time_us = imu.time_usec;
            link->imu_msgs++;
            updates++;
        }
        link->parse_errors = status.parse_error;

        if ((size_t)n < sizeof(buf)) {
            break;
        }
    }

    return updates;
}

int mavlink_link_send_rates(MavlinkLink *link, const GuidanceSetpoints *sp,
                            float thrust, uint32_t boot_ms)
{
    if (link->fd < 0) {
        return -1;
    }

    mavlink_set_attitude_target_t target;
    memset(&target, 0, sizeof(target));
    target.time_boot_ms = boot_ms;
    target.target_system = link->target_sysid;
    target.target_component = link->target_compid;

    /* Керуємо ВИКЛЮЧНО кутовими швидкостями, тому автопілоту наказано
     * ігнорувати поле орієнтації. Біти 0..2 (ROLL/PITCH/YAW_RATE_IGNORE)
     * лишаються нульовими — інакше він викинув би саме те, що ми шлемо. */
    target.type_mask = ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE;

    /* Кватерніон однаково ігнорується, але має лишатися одиничним:
     * автопілоти перевіряють норму ще до розбору маски. */
    target.q[0] = 1.0f;
    target.q[1] = 0.0f;
    target.q[2] = 0.0f;
    target.q[3] = 0.0f;

    target.body_roll_rate = 0.0f;    /* крен тримає контур стабілізації горизонту */
    target.body_pitch_rate = sp->pitch_rate_rad_s;
    target.body_yaw_rate = sp->yaw_rate_rad_s;
    target.thrust = (thrust < 0.0f) ? 0.0f : (thrust > 1.0f ? 1.0f : thrust);

    mavlink_message_t msg;
    mavlink_msg_set_attitude_target_encode(link->sysid, link->compid, &msg, &target);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    const uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);

    /* UART віддає не все одразу; недописаний пакет автопілот відкине
     * за контрольною сумою, тож дописуємо хвіст. */
    size_t sent = 0;
    while (sent < len) {
        const ssize_t n = write(link->fd, buf + sent, (size_t)len - sent);
        if (n > 0) {
            sent += (size_t)n;
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            /* Буфер драйвера забитий: така уставка все одно застаріє
             * за 10 мс, наступний такт надішле свіжу. */
            return -1;
        }
        perror("mavlink: write");
        return -1;
    }

    return 0;
}

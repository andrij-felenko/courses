#define _POSIX_C_SOURCE 200809L

#include "link.h"

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

uint64_t now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000u + (uint64_t)(ts.tv_nsec / 1000);
}

int link_open(link_t *l, uint16_t local_port)
{
    memset(l, 0, sizeof(*l));
    l->fd = -1;
    l->sys_id = 255;                            /* окремий ідентифікатор станції, не автопілота */
    l->comp_id = MAV_COMP_ID_ONBOARD_COMPUTER;
    l->target_sys = 1;
    l->target_comp = MAV_COMP_ID_AUTOPILOT1;

    const int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    /* Неблокувальний сокет: увесь контроль часу тримає poll(), а не ядро. */
    const int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0 || fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("fcntl");
        close(fd);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(local_port);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(fd);
        return -1;
    }

    l->fd = fd;
    l->peer_len = sizeof(l->peer);
    return 0;
}

void link_close(link_t *l)
{
    if (l->fd >= 0) {
        close(l->fd);
        l->fd = -1;
    }
}

int link_send(link_t *l, const mavlink_message_t *msg)
{
    if (l->fd < 0 || !l->peer_known) return -1;

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    const uint16_t len = mavlink_msg_to_send_buffer(buf, msg);

    for (;;) {
        const ssize_t n = sendto(l->fd, buf, len, 0,
                                 (const struct sockaddr *)&l->peer, l->peer_len);
        if (n == (ssize_t)len) return 0;
        if (n < 0 && errno == EINTR) continue;
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            /* Черга сокета переповнена. Уставку губимо свідомо:
               наступний тік потоку буде за 50 мс, а блокувати цикл не можна. */
            return -1;
        }
        perror("sendto");
        return -1;
    }
}

static void handle_message(link_t *l, const mavlink_message_t *msg)
{
    switch (msg->msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {
        /* Б'ються серцем і камери, і гімбали — нас цікавить лише автопілот. */
        if (msg->compid != MAV_COMP_ID_AUTOPILOT1) return;
        mavlink_heartbeat_t hb;
        mavlink_msg_heartbeat_decode(msg, &hb);
        l->target_sys = msg->sysid;
        l->tlm.base_mode = hb.base_mode;
        l->tlm.custom_mode = hb.custom_mode;
        l->tlm.system_status = hb.system_status;
        l->tlm.heartbeat_us = now_us();
        l->tlm.have_heartbeat = 1;
        break;
    }
    case MAVLINK_MSG_ID_COMMAND_ACK: {
        mavlink_command_ack_t ack;
        mavlink_msg_command_ack_decode(msg, &ack);
        l->ack_command = ack.command;
        l->ack_result = ack.result;
        l->ack_valid = 1;
        break;
    }
    case MAVLINK_MSG_ID_LOCAL_POSITION_NED: {
        mavlink_local_position_ned_t p;
        mavlink_msg_local_position_ned_decode(msg, &p);
        l->tlm.x = p.x; l->tlm.y = p.y; l->tlm.z = p.z;
        l->tlm.vx = p.vx; l->tlm.vy = p.vy; l->tlm.vz = p.vz;
        l->tlm.position_us = now_us();
        l->tlm.have_position = 1;
        break;
    }
    case MAVLINK_MSG_ID_ATTITUDE: {
        mavlink_attitude_t a;
        mavlink_msg_attitude_decode(msg, &a);
        l->tlm.roll = a.roll; l->tlm.pitch = a.pitch; l->tlm.yaw = a.yaw;
        l->tlm.rollspeed = a.rollspeed;
        l->tlm.pitchspeed = a.pitchspeed;
        l->tlm.yawspeed = a.yawspeed;
        l->tlm.have_attitude = 1;
        break;
    }
    case MAVLINK_MSG_ID_ESTIMATOR_STATUS: {
        mavlink_estimator_status_t e;
        mavlink_msg_estimator_status_decode(msg, &e);
        l->tlm.estimator_flags = e.flags;
        l->tlm.have_estimator = 1;
        break;
    }
    default:
        break;
    }
}

int link_poll(link_t *l, int timeout_ms)
{
    int count = 0;
    int waited = 0;

    for (;;) {
        struct pollfd pfd;
        pfd.fd = l->fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        const int rc = poll(&pfd, 1, waited ? 0 : timeout_ms);
        if (rc < 0) {
            if (errno == EINTR) continue;
            perror("poll");
            return -1;
        }
        waited = 1;
        if (rc == 0) return count;

        uint8_t buf[2048];
        struct sockaddr_in from;
        socklen_t from_len = sizeof(from);
        const ssize_t n = recvfrom(l->fd, buf, sizeof(buf), 0,
                                   (struct sockaddr *)&from, &from_len);
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return count;
            perror("recvfrom");
            return -1;
        }

        if (!l->peer_known) {
            /* Адресу автопілота дізнаємось із першого ж кадру: так само
               працює udp://:14540 у наземних станціях. */
            l->peer = from;
            l->peer_len = from_len;
            l->peer_known = 1;
        }

        for (ssize_t i = 0; i < n; ++i) {
            mavlink_message_t msg;
            mavlink_status_t status;
            /* MAVLINK_COMM_0 — глобальний стан розбору; на один канал цього досить. */
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) == 1) {
                handle_message(l, &msg);
                ++count;
            }
        }
    }
}

int link_wait_heartbeat(link_t *l, int timeout_ms)
{
    const uint64_t deadline = now_us() + (uint64_t)timeout_ms * 1000u;
    while (now_us() < deadline) {
        if (link_poll(l, 100) < 0) return -1;
        if (l->tlm.have_heartbeat) return 0;
    }
    return -1;
}

int link_heartbeat_tick(link_t *l)
{
    const uint64_t t = now_us();
    if (l->our_heartbeat_us != 0 && t - l->our_heartbeat_us < 1000000u) return 0;

    mavlink_message_t msg;
    mavlink_msg_heartbeat_pack(l->sys_id, l->comp_id, &msg,
                               MAV_TYPE_ONBOARD_CONTROLLER, MAV_AUTOPILOT_INVALID,
                               0, 0, MAV_STATE_ACTIVE);
    l->our_heartbeat_us = t;
    return link_send(l, &msg);
}

int link_command(link_t *l, uint16_t command, const float params[7], uint8_t confirmation)
{
    mavlink_command_long_t cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.target_system = l->target_sys;
    cmd.target_component = l->target_comp;
    cmd.command = command;
    cmd.confirmation = confirmation;
    cmd.param1 = params[0];
    cmd.param2 = params[1];
    cmd.param3 = params[2];
    cmd.param4 = params[3];
    cmd.param5 = params[4];
    cmd.param6 = params[5];
    cmd.param7 = params[6];

    /* Підтвердження попередньої спроби тієї ж команди більше не рахуємо. */
    if (l->ack_valid && l->ack_command == command) l->ack_valid = 0;

    mavlink_message_t msg;
    mavlink_msg_command_long_encode(l->sys_id, l->comp_id, &msg, &cmd);
    return link_send(l, &msg);
}

int link_take_ack(link_t *l, uint16_t command, uint8_t *result)
{
    if (!l->ack_valid || l->ack_command != command) return 0;
    *result = l->ack_result;
    l->ack_valid = 0;
    return 1;
}

const char *mav_result_name(uint8_t result)
{
    switch (result) {
    case MAV_RESULT_ACCEPTED:              return "ACCEPTED";
    case MAV_RESULT_TEMPORARILY_REJECTED:  return "TEMPORARILY_REJECTED";
    case MAV_RESULT_DENIED:                return "DENIED";
    case MAV_RESULT_UNSUPPORTED:           return "UNSUPPORTED";
    case MAV_RESULT_FAILED:                return "FAILED";
    default:                               return "невідомий код";
    }
}

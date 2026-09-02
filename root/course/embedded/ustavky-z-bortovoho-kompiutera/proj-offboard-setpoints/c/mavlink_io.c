#include "mavlink_io.h"

#include <string.h>

#include <common/mavlink.h>

#include "serial.h"

/* Наш власний ідентифікатор бачить автопілот; ціль — завжди борт №1. */
#define TARGET_SYS_ID 1
#define TX_TIMEOUT_MS 5

/* PX4 пакує головний режим у байти 16-23 поля custom_mode. */
#define PX4_MAIN_MODE_OFFBOARD 6

/* У type_mask одиниця означає «поле ігнорувати». Гасимо позицію
 * (біти 0-2), прискорення (біти 6-8) і yaw_rate (біт 11) — лишаються
 * швидкості vx/vy/vz та кут yaw. */
#define SETPOINT_MASK_VELOCITY_YAW 0x09C7

static int send_msg(int fd, const mavlink_message_t *msg) {
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, msg);
    return serial_write_all(fd, buf, len, TX_TIMEOUT_MS);
}

int mav_send_setpoint(int fd, uint8_t sys_id, uint8_t comp_id,
                      float vx, float vy, float vz, float yaw) {
    mavlink_set_position_target_local_ned_t sp;
    memset(&sp, 0, sizeof(sp));

    /* Час завантаження нам невідомий, і PX4 його не вимагає: він бере
     * власний штамп у момент прийому кадру. */
    sp.time_boot_ms = 0;
    sp.target_system = TARGET_SYS_ID;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;
    sp.type_mask = SETPOINT_MASK_VELOCITY_YAW;
    sp.vx = vx;
    sp.vy = vy;
    sp.vz = vz;
    sp.yaw = yaw;

    mavlink_message_t msg;
    mavlink_msg_set_position_target_local_ned_encode(sys_id, comp_id, &msg, &sp);
    return send_msg(fd, &msg);
}

int mav_send_offboard_request(int fd, uint8_t sys_id, uint8_t comp_id) {
    mavlink_command_long_t cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.target_system = TARGET_SYS_ID;
    cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
    cmd.command = MAV_CMD_DO_SET_MODE;
    cmd.confirmation = 0;
    cmd.param1 = (float)MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
    cmd.param2 = (float)PX4_MAIN_MODE_OFFBOARD;
    cmd.param3 = 0.0f; /* підрежиму в Offboard немає */

    mavlink_message_t msg;
    mavlink_msg_command_long_encode(sys_id, comp_id, &msg, &cmd);
    return send_msg(fd, &msg);
}

int mav_send_heartbeat(int fd, uint8_t sys_id, uint8_t comp_id) {
    mavlink_message_t msg;
    mavlink_msg_heartbeat_pack(sys_id, comp_id, &msg,
                               MAV_TYPE_ONBOARD_CONTROLLER,
                               MAV_AUTOPILOT_INVALID, /* ми не автопілот */
                               0, 0, MAV_STATE_ACTIVE);
    return send_msg(fd, &msg);
}

static void handle_message(const mavlink_message_t *msg, fcu_status_t *st,
                           uint64_t now_ms) {
    /* Нас цікавить лише автопілот борта №1: у джгуті висять ще
     * камера, дальномір і наземна станція через радіомодем. */
    if (msg->sysid != TARGET_SYS_ID || msg->compid != MAV_COMP_ID_AUTOPILOT1) {
        return;
    }

    switch (msg->msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {
        mavlink_heartbeat_t hb;
        mavlink_msg_heartbeat_decode(msg, &hb);
        st->link_alive = true;
        st->last_heartbeat_ms = now_ms;
        st->armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
        st->offboard = (hb.base_mode & MAV_MODE_FLAG_CUSTOM_MODE_ENABLED) != 0 &&
                       ((hb.custom_mode >> 16) & 0xFFu) == PX4_MAIN_MODE_OFFBOARD;
        break;
    }
    case MAVLINK_MSG_ID_COMMAND_ACK: {
        mavlink_command_ack_t ack;
        mavlink_msg_command_ack_decode(msg, &ack);
        if (ack.command == MAV_CMD_DO_SET_MODE) {
            st->mode_ack_seen = true;
            st->mode_ack_result = ack.result;
            st->mode_ack_ok = (ack.result == MAV_RESULT_ACCEPTED);
        }
        break;
    }
    default:
        break;
    }
}

void mav_poll(int fd, fcu_status_t *st, uint64_t now_ms) {
    uint8_t buf[512];
    mavlink_message_t msg;
    mavlink_status_t status;

    /* Обмежуємо роботу за такт: якщо на лінії потоп із телеметрії,
     * розбір не має права з'їсти весь такт RT-циклу. */
    for (int chunk = 0; chunk < 4; ++chunk) {
        ssize_t n = serial_read_available(fd, buf, sizeof(buf));
        if (n <= 0) {
            break;
        }
        for (ssize_t i = 0; i < n; ++i) {
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) == 1) {
                handle_message(&msg, st, now_ms);
            }
        }
        st->rx_drops = status.packet_rx_drop_count;
        if ((size_t)n < sizeof(buf)) {
            break;
        }
    }
}

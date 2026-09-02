#include "mavlink_link.hpp"

#include <array>

namespace {

constexpr std::uint8_t kTargetSysId = 1;  // борт: автопілот завжди №1
constexpr std::uint8_t kPx4MainModeOffboard = 6;
constexpr auto kTxTimeout = std::chrono::milliseconds(5);

// У type_mask одиниця означає «поле ігнорувати». Гасимо позицію
// (біти 0-2), прискорення (біти 6-8) і yaw_rate (біт 11) — лишаються
// швидкості vx/vy/vz та кут yaw.
constexpr std::uint16_t kMaskVelocityYaw = 0x09C7;

}  // namespace

MavlinkLink::MavlinkLink(const std::string& port, speed_t baud,
                         std::uint8_t sys_id, std::uint8_t comp_id)
    : port_(port, baud), sys_id_(sys_id), comp_id_(comp_id) {}

namespace {

TxResult send_message(SerialPort& port, const mavlink_message_t& msg) {
    std::array<std::uint8_t, MAVLINK_MAX_PACKET_LEN> buffer{};
    const std::uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &msg);
    return port.write_all(std::span<const std::uint8_t>(buffer).first(len), kTxTimeout);
}

}  // namespace

TxResult MavlinkLink::send_setpoint(const VelocityCommand& cmd) {
    mavlink_set_position_target_local_ned_t sp{};
    // Власний штамп часу PX4 не потрібен: він бере час прийому кадру.
    sp.time_boot_ms = 0;
    sp.target_system = kTargetSysId;
    sp.target_component = MAV_COMP_ID_AUTOPILOT1;
    sp.coordinate_frame = MAV_FRAME_LOCAL_NED;
    sp.type_mask = kMaskVelocityYaw;
    sp.vx = cmd.vx;
    sp.vy = cmd.vy;
    sp.vz = cmd.vz;
    sp.yaw = cmd.yaw;

    mavlink_message_t msg{};
    mavlink_msg_set_position_target_local_ned_encode(sys_id_, comp_id_, &msg, &sp);
    return send_message(port_, msg);
}

TxResult MavlinkLink::request_offboard() {
    mavlink_command_long_t cmd{};
    cmd.target_system = kTargetSysId;
    cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
    cmd.command = MAV_CMD_DO_SET_MODE;
    cmd.confirmation = 0;
    cmd.param1 = static_cast<float>(MAV_MODE_FLAG_CUSTOM_MODE_ENABLED);
    cmd.param2 = static_cast<float>(kPx4MainModeOffboard);
    cmd.param3 = 0.0f;  // підрежиму в Offboard немає

    mavlink_message_t msg{};
    mavlink_msg_command_long_encode(sys_id_, comp_id_, &msg, &cmd);
    return send_message(port_, msg);
}

TxResult MavlinkLink::send_heartbeat() {
    mavlink_message_t msg{};
    mavlink_msg_heartbeat_pack(sys_id_, comp_id_, &msg,
                               MAV_TYPE_ONBOARD_CONTROLLER,
                               MAV_AUTOPILOT_INVALID,  // ми не автопілот
                               0, 0, MAV_STATE_ACTIVE);
    return send_message(port_, msg);
}

void MavlinkLink::handle(const mavlink_message_t& msg) {
    // У джгуті висять ще камера, дальномір і радіомодем наземної станції:
    // слухаємо лише автопілот борта.
    if (msg.sysid != kTargetSysId || msg.compid != MAV_COMP_ID_AUTOPILOT1) {
        return;
    }

    switch (msg.msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {
        mavlink_heartbeat_t hb{};
        mavlink_msg_heartbeat_decode(&msg, &hb);
        status_.last_heartbeat = std::chrono::steady_clock::now();
        status_.armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
        // PX4 пакує головний режим у байти 16-23 поля custom_mode.
        status_.offboard = (hb.base_mode & MAV_MODE_FLAG_CUSTOM_MODE_ENABLED) != 0 &&
                           ((hb.custom_mode >> 16) & 0xFFu) == kPx4MainModeOffboard;
        break;
    }
    case MAVLINK_MSG_ID_COMMAND_ACK: {
        mavlink_command_ack_t ack{};
        mavlink_msg_command_ack_decode(&msg, &ack);
        if (ack.command == MAV_CMD_DO_SET_MODE) {
            mode_ack_ = ModeAck{ack.result == MAV_RESULT_ACCEPTED, ack.result};
        }
        break;
    }
    default:
        break;
    }
}

const FcuStatus& MavlinkLink::poll() {
    std::array<std::uint8_t, 512> buffer{};

    // Обмежуємо роботу за такт: потоп телеметрії не має права з'їсти
    // весь такт RT-циклу.
    for (int chunk = 0; chunk < 4; ++chunk) {
        const auto data = port_.read_some(buffer);
        if (data.empty()) {
            break;
        }
        for (const std::uint8_t byte : data) {
            mavlink_message_t msg{};
            if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &parse_status_) == 1) {
                handle(msg);
            }
        }
        status_.rx_drops = parse_status_.packet_rx_drop_count;
        if (data.size() < buffer.size()) {
            break;
        }
    }
    return status_;
}

std::optional<ModeAck> MavlinkLink::take_mode_ack() {
    std::optional<ModeAck> ack;
    ack.swap(mode_ack_);
    return ack;
}

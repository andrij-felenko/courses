// receiver_cpp.hpp — Ідіоматичний обробник та диспетчер на C++
#pragma once
#include <functional>
#include <span>
#include <array>
#include "smart_multispectral/mavlink.h"

class MavlinkCommandDispatcher {
public:
    using CaptureCallback = std::function<bool(uint32_t exposure_ms, uint8_t filter_mode)>;

    MavlinkCommandDispatcher(uint8_t sys_id, uint8_t comp_id)
        : sys_id_(sys_id), comp_id_(comp_id) {}

    void set_capture_handler(CaptureCallback handler) {
        capture_handler_ = std::move(handler);
    }

    template <typename TransmitFn>
    void feed_byte(uint8_t byte, TransmitFn&& transmit_fn) {
        mavlink_message_t msg;
        mavlink_status_t status;

        if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status)) {
            dispatch_message(msg, transmit_fn);
        }
    }

private:
    template <typename TransmitFn>
    void dispatch_message(const mavlink_message_t& msg, TransmitFn&& transmit_fn) {
        if (msg.msgid == MAVLINK_MSG_ID_COMMAND_LONG) {
            mavlink_command_long_t cmd;
            mavlink_msg_command_long_decode(&msg, &cmd);

            if (cmd.target_system != sys_id_ && cmd.target_system != 0) return;
            if (cmd.target_component != comp_id_ && cmd.target_component != 0) return;

            uint8_t result = MAV_RESULT_UNSUPPORTED;
            if (cmd.command == 42050 && capture_handler_) {
                const bool ok = capture_handler_(
                    static_cast<uint32_t>(cmd.param1),
                    static_cast<uint8_t>(cmd.param2)
                );
                result = ok ? MAV_RESULT_ACCEPTED : MAV_RESULT_FAILED;
            }

            mavlink_message_t ack_msg;
            std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> buffer;
            mavlink_msg_command_ack_pack(
                sys_id_, comp_id_, &ack_msg,
                cmd.command, result, 0, 0,
                msg.sysid, msg.compid
            );

            const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &ack_msg);
            transmit_fn(std::span<const uint8_t>(buffer.data(), len));
        }
    }

    uint8_t sys_id_;
    uint8_t comp_id_;
    CaptureCallback capture_handler_;
};

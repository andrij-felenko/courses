#include <mavlink.h>
#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>

class MavlinkCommander {
public:
    using KeyArray = std::array<uint8_t, 32>;

    explicit MavlinkCommander(const KeyArray& key, uint8_t link_id = 0)
        : key_(key), link_id_(link_id) {
        signing_ctx_ = {};
        streams_ = {};

        signing_ctx_.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
        signing_ctx_.link_id = link_id_;
        signing_ctx_.timestamp = 125000000ULL;
        std::memcpy(signing_ctx_.secret_key, key_.data(), key_.size());
        signing_ctx_.streams = &streams_;
    }

    std::vector<uint8_t> createSignedArmCommand(uint8_t channel, uint8_t target_sys, uint8_t target_comp) {
        mavlink_message_t msg;
        mavlink_command_long_t cmd{};
        cmd.target_system = target_sys;
        cmd.target_component = target_comp;
        cmd.command = MAV_CMD_COMPONENT_ARM_DISARM;
        cmd.confirmation = 0;
        cmd.param1 = 1.0f; // ARM

        mavlink_msg_command_long_encode(255, 190, &msg, &cmd);

        auto* status = mavlink_get_channel_status(channel);
        status->signing = &signing_ctx_;
        status->signing_streams = &streams_;

        std::vector<uint8_t> buffer(MAVLINK_MAX_PACKET_LEN);
        const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &msg);
        buffer.resize(len);
        return buffer;
    }

private:
    KeyArray key_;
    uint8_t link_id_;
    mavlink_signing_t signing_ctx_{};
    mavlink_signing_streams_t streams_{};
};

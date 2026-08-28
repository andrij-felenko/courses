#include <mavlink.h>
#include <array>
#include <span>
#include <cstdint>

class HighLatencyController {
public:
    static mavlink_message_t createControlCommand(uint8_t target_sys, uint8_t target_comp, bool enable) noexcept {
        mavlink_message_t msg{};
        mavlink_command_long_t cmd{};

        cmd.target_system    = target_sys;
        cmd.target_component = target_comp;
        cmd.command          = MAV_CMD_CONTROL_HIGH_LATENCY;
        cmd.confirmation     = 0;
        cmd.param1           = enable ? 1.0f : 0.0f;

        mavlink_msg_command_long_encode(255, 190, &msg, &cmd);
        return msg;
    }
};

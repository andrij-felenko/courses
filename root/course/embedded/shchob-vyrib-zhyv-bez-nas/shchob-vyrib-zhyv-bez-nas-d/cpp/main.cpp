#include <string_view>
#include <string>
#include <cstdint>
#include <format>
#include <expected>

namespace local_api {

enum class CommandError {
    InvalidJson,
    UnknownCommand,
    InvalidParameter,
    BufferOverflow
};

struct DeviceState {
    bool relay_state{false};
    int16_t temperature_c_x10{225}; // 22.5 C
    uint32_t uptime_sec{0};
};

class CommandDispatcher {
public:
    explicit CommandDispatcher(DeviceState& state) noexcept : state_(state) {}

    [[nodiscard]] std::expected<std::string, CommandError> process_command(std::string_view payload) {
        if (payload.contains("\"cmd\":\"get_status\"")) {
            return std::format(
                R"({{"status":"ok","relay":{},"temp":{:.1f},"uptime":{}}})",
                state_.relay_state ? "true" : "false",
                state_.temperature_c_x10 / 10.0,
                state_.uptime_sec
            );
        }

        if (payload.contains("\"cmd\":\"set_relay\"")) {
            if (payload.contains("\"state\":true")) {
                state_.relay_state = true;
                apply_hardware_relay(true);
            } else if (payload.contains("\"state\":false")) {
                state_.relay_state = false;
                apply_hardware_relay(false);
            } else {
                return std::unexpected(CommandError::InvalidParameter);
            }

            return std::format(
                R"({{"status":"ok","relay":{}}})",
                state_.relay_state ? "true" : "false"
            );
        }

        return std::unexpected(CommandError::UnknownCommand);
    }

private:
    void apply_hardware_relay(bool enable) noexcept {
        // Прямий виклик апаратного драйвера GPIO
    }

    DeviceState& state_;
};

} // namespace local_api

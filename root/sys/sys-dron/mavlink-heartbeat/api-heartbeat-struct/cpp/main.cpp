#include <iostream>
#include <cstdint>
#include <span>
#include <optional>
#include <string_view>

namespace mavlink {

struct HeartbeatData {
    uint32_t custom_mode{0};
    uint8_t  type{0};
    uint8_t  autopilot{0};
    uint8_t  base_mode{0};
    uint8_t  system_status{0};
    uint8_t  mavlink_version{3};

    [[nodiscard]] constexpr bool is_armed() const noexcept {
        return (base_mode & 0x80) != 0;
    }

    [[nodiscard]] constexpr bool is_manual_input_enabled() const noexcept {
        return (base_mode & 0x40) != 0;
    }

    [[nodiscard]] constexpr bool is_stabilize_enabled() const noexcept {
        return (base_mode & 0x10) != 0;
    }

    [[nodiscard]] constexpr bool is_guided_enabled() const noexcept {
        return (base_mode & 0x08) != 0;
    }

    [[nodiscard]] constexpr bool is_auto_enabled() const noexcept {
        return (base_mode & 0x04) != 0;
    }

    [[nodiscard]] constexpr bool is_custom_mode_valid() const noexcept {
        return (base_mode & 0x01) != 0;
    }

    [[nodiscard]] static std::optional<HeartbeatData> deserialize(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 9) {
            return std::nullopt;
        }

        HeartbeatData data;
        data.custom_mode = static_cast<uint32_t>(buffer[0]) |
                          (static_cast<uint32_t>(buffer[1]) << 8) |
                          (static_cast<uint32_t>(buffer[2]) << 16) |
                          (static_cast<uint32_t>(buffer[3]) << 24);

        data.type            = buffer[4];
        data.autopilot       = buffer[5];
        data.base_mode       = buffer[6];
        data.system_status   = buffer[7];
        data.mavlink_version = buffer[8];

        return data;
    }

    void serialize_into(std::span<uint8_t, 9> buffer) const noexcept {
        buffer[0] = static_cast<uint8_t>(custom_mode & 0xFF);
        buffer[1] = static_cast<uint8_t>((custom_mode >> 8) & 0xFF);
        buffer[2] = static_cast<uint8_t>((custom_mode >> 16) & 0xFF);
        buffer[3] = static_cast<uint8_t>((custom_mode >> 24) & 0xFF);

        buffer[4] = type;
        buffer[5] = autopilot;
        buffer[6] = base_mode;
        buffer[7] = system_status;
        buffer[8] = mavlink_version;
    }
};

} // namespace mavlink

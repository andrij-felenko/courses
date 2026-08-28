// Ідіоматична обгортка структури HEARTBEAT у C++20
struct MavlinkHeartbeat {
    uint32_t custom_mode{0};
    uint8_t  type{0};
    uint8_t  autopilot{0};
    uint8_t  base_mode{0};
    uint8_t  system_status{0};
    uint8_t  mavlink_version{3};

    [[nodiscard]] constexpr bool isArmed() const noexcept {
        return (base_mode & 0x80) != 0; // MAV_MODE_FLAG_SAFETY_ARMED
    }

    [[nodiscard]] constexpr bool isAuto() const noexcept {
        return (base_mode & 0x04) != 0; // MAV_MODE_FLAG_AUTO_ENABLED
    }

    [[nodiscard]] constexpr bool isGuided() const noexcept {
        return (base_mode & 0x08) != 0; // MAV_MODE_FLAG_GUIDED_ENABLED
    }
};

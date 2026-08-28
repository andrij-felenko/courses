// Бортовий захист від застигання осей MAVLink MANUAL_CONTROL (C++20)
#include <cstdint>
#include <algorithm>

struct AxisCommands {
    int16_t roll{0};
    int16_t pitch{0};
    int16_t throttle{0};
    int16_t yaw{0};
};

constexpr void processManualControlTimeout(AxisCommands& cmd, uint32_t last_packet_ms, uint32_t now_ms) noexcept {
    const uint32_t dt = now_ms - last_packet_ms;
    
    if (dt > 250 && dt <= 1000) {
        cmd.roll = 0;
        cmd.pitch = 0;
        cmd.yaw = 0;
        cmd.throttle = 500; // Режим утримання висоти
    } else if (dt > 1000) {
        cmd.roll = 0;
        cmd.pitch = 0;
        cmd.yaw = 0;
        cmd.throttle = 0;   // Аварійне відключення / Failsafe
    }
}

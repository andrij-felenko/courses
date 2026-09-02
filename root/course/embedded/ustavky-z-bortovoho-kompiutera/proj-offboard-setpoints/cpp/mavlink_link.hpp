#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <string>
#include <system_error>

#include <common/mavlink.h>

#include "serial_port.hpp"

// Ціль керування в локальній системі NED плюс абсолютний курс.
struct VelocityCommand {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};
    float yaw{0.0f};
};

// Знімок того, що автопілот розповів про себе своїми ж повідомленнями.
struct FcuStatus {
    std::optional<std::chrono::steady_clock::time_point> last_heartbeat;
    bool offboard{false};
    bool armed{false};
    std::uint32_t rx_drops{0};
};

// Результат COMMAND_ACK на наш DO_SET_MODE.
struct ModeAck {
    bool accepted{false};
    std::uint8_t result{0};  // сирий MAV_RESULT для журналу
};

using TxResult = std::expected<void, std::error_code>;

class MavlinkLink {
public:
    MavlinkLink(const std::string& port, speed_t baud,
                std::uint8_t sys_id, std::uint8_t comp_id);

    [[nodiscard]] TxResult send_setpoint(const VelocityCommand& cmd);
    [[nodiscard]] TxResult request_offboard();
    [[nodiscard]] TxResult send_heartbeat();

    // Розбирає все, що встигло прийти, і повертає оновлений знімок.
    const FcuStatus& poll();

    // Забирає підтвердження режиму: другий раз той самий ACK не віддасть.
    std::optional<ModeAck> take_mode_ack();

private:
    void handle(const mavlink_message_t& msg);

    SerialPort port_;
    std::uint8_t sys_id_;
    std::uint8_t comp_id_;
    mavlink_status_t parse_status_{};
    FcuStatus status_{};
    std::optional<ModeAck> mode_ack_{};
};

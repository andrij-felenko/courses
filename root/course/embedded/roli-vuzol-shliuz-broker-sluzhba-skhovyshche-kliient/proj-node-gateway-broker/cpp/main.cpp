#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

enum class FrameType : uint8_t {
    Telemetry = 0x01,
    Command   = 0x02,
    Ack       = 0x03
};

#pragma pack(push, 1)
struct TelemetryFrame {
    uint8_t   magic{0xAA};
    FrameType type{FrameType::Telemetry};
    uint16_t  node_id{0};
    uint32_t  seq_num{0};
    int16_t   temperature_c_celsius{0};
    uint16_t  battery_mv{0};
    uint8_t   flags{0};
    uint8_t   reserved{0};
    uint16_t  crc16{0};
};

struct CommandFrame {
    uint8_t   magic{0xAA};
    FrameType type{FrameType::Command};
    uint16_t  node_id{0};
    uint32_t  seq_num{0};
    uint8_t   command_id{0};
    uint8_t   payload_val{0};
    uint16_t  crc16{0};
};
#pragma pack(pop)

class Crc16Ccitt {
public:
    static constexpr uint16_t calculate(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }
};

class EdgeNode {
public:
    explicit constexpr EdgeNode(uint16_t id) noexcept : node_id_(id) {}

    [[nodiscard]] TelemetryFrame generate_telemetry(int16_t temp_c, uint16_t bat_mv, uint8_t flags) noexcept {
        TelemetryFrame frame{};
        frame.magic = 0xAA;
        frame.type = FrameType::Telemetry;
        frame.node_id = node_id_;
        frame.seq_num = ++seq_counter_;
        frame.temperature_c_celsius = temp_c;
        frame.battery_mv = bat_mv;
        frame.flags = flags;
        frame.reserved = 0x00;

        auto raw_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&frame),
            sizeof(TelemetryFrame) - sizeof(uint16_t)
        );
        frame.crc16 = Crc16Ccitt::calculate(raw_bytes);
        return frame;
    }

    [[nodiscard]] bool handle_command(std::span<const uint8_t> raw_cmd) noexcept {
        if (raw_cmd.size() < sizeof(CommandFrame)) {
            return false;
        }
        const auto* cmd = reinterpret_cast<const CommandFrame*>(raw_cmd.data());
        if (cmd->magic != 0xAA || cmd->type != FrameType::Command || cmd->node_id != node_id_) {
            return false;
        }
        auto payload_span = raw_cmd.first(sizeof(CommandFrame) - sizeof(uint16_t));
        if (cmd->crc16 != Crc16Ccitt::calculate(payload_span)) {
            return false;
        }

        if (cmd->command_id == 0x10) { // Set relay
            relay_state_ = (cmd->payload_val != 0);
            return true;
        }
        return false;
    }

    [[nodiscard]] bool is_relay_on() const noexcept { return relay_state_; }
    [[nodiscard]] uint16_t id() const noexcept { return node_id_; }

private:
    uint16_t node_id_;
    uint32_t seq_counter_{0};
    bool relay_state_{false};
};

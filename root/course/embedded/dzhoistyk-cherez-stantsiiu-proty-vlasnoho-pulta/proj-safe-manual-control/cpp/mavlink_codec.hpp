#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <variant>

namespace mavlink {

/* Кодек рівно під потрібні повідомлення: HEARTBEAT #0, MANUAL_CONTROL #69,
 * COMMAND_LONG #76 і COMMAND_ACK #77 на відповідь. Розбираються обидві версії
 * кадру — v1 (0xFE) і v2 (0xFD), із підписом і з обрізанням хвостових нулів. */

inline constexpr std::size_t   kMaxPayload   = 255;
inline constexpr std::size_t   kSignatureLen = 13;
inline constexpr std::byte     kStxV1{0xFE};
inline constexpr std::byte     kStxV2{0xFD};

inline constexpr std::uint32_t kMsgHeartbeat     = 0;
inline constexpr std::uint32_t kMsgManualControl = 69;
inline constexpr std::uint32_t kMsgCommandLong   = 76;
inline constexpr std::uint32_t kMsgCommandAck    = 77;

inline constexpr std::uint16_t kCmdComponentArmDisarm = 400;

enum class Result : std::uint8_t {
    Accepted = 0, TemporarilyRejected = 1, Denied = 2, Unsupported = 3, Failed = 4
};

inline constexpr std::uint8_t kCompAutopilot1     = 1;
inline constexpr std::uint8_t kCompMissionPlanner = 190;
inline constexpr std::uint8_t kCompAll            = 0;

struct Heartbeat {
    std::uint32_t customMode{};
    std::uint8_t  type{}, autopilot{}, baseMode{}, systemStatus{}, mavlinkVersion{};
};

struct ManualControl {
    std::int16_t  x{}, y{}, z{}, r{};
    std::uint16_t buttons{};
    std::uint8_t  target{};
};

struct CommandLong {
    std::array<float, 7> param{};
    std::uint16_t        command{};
    std::uint8_t         targetSystem{}, targetComponent{}, confirmation{};
};

struct CommandAck {
    std::uint16_t command{};
    Result        result{Result::Accepted};
};

// Тег у кадрі замінено типом: розбір повертає варіант, а не void* із switch.
using Message = std::variant<Heartbeat, ManualControl, CommandLong, CommandAck>;

struct Frame {
    std::uint8_t  sysid{}, compid{}, seq{};
    std::uint32_t msgid{};
    std::uint8_t  len{};                         // стільки байтів реально прийшло
    std::array<std::byte, kMaxPayload> payload{}; // хвіст добито нулями
};

// Порожній optional — кадр не нашого діалекту.
[[nodiscard]] std::optional<Message> decode(const Frame& f) noexcept;

// Збирає кадр v2 у наданий буфер; 0 — не влізло.
[[nodiscard]] std::size_t encode(std::span<std::byte> out, const Message& msg,
                                 std::uint8_t sysid, std::uint8_t compid, std::uint8_t seq) noexcept;

class Parser {
public:
    struct Stats {
        std::uint32_t frames{};
        std::uint32_t crcErrors{};    // шум в ефірі або обрив посеред кадру
        std::uint32_t unknown{};      // повідомлення поза нашим діалектом
        std::uint32_t unsupported{};  // нерозпізнані incompat-прапорці
    };

    // Повертає кадр рівно тоді, коли байт завершив цілий і CRC-коректний пакет.
    [[nodiscard]] std::optional<Frame> push(std::byte b) noexcept;

    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    enum class Stage : std::uint8_t {
        Idle, Len, Incompat, Compat, Seq, Sysid, Compid, Msgid1, Msgid2, Msgid3, Payload, Crc1, Crc2
    };

    void enterPayload() noexcept;

    Stage         stage_{Stage::Idle};
    bool          isV2_{false};
    std::uint8_t  incompat_{}, seq_{}, sysid_{}, compid_{}, len_{}, idx_{}, skip_{};
    std::uint32_t msgid_{};
    std::uint16_t crc_{}, rxCrc_{};
    std::array<std::byte, kMaxPayload> payload_{};
    Stats stats_{};
};

}  // namespace mavlink

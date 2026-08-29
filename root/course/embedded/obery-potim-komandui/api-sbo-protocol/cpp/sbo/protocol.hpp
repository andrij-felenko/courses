// Профіль Select-Before-Operate: типи дроту та кодек кадру (C++23).
#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace sbo {

using Ms = std::chrono::milliseconds;

// --- Розділ 1: розкладка кадру ---------------------------------------
inline constexpr std::uint8_t  kMagic = 0x5B;      // ASCII '['
inline constexpr std::size_t   kHeaderLen = 16;
inline constexpr std::size_t   kCrcLen = 2;
inline constexpr std::size_t   kMaxPayload = 128;
inline constexpr std::size_t   kMaxFrame = kHeaderLen + kMaxPayload + kCrcLen;

inline constexpr std::uint8_t kAddrBroadcast = 0xFF;
inline constexpr std::uint8_t kAddrGcs = 0xFE;
inline constexpr std::uint8_t kAddrRelay = 0xFD;

enum class Comp : std::uint8_t { Fc = 0x01, Esc = 0x02, Nav = 0x03 };

// --- Розділ 2: типи повідомлень ---------------------------------------
enum class MsgType : std::uint8_t {
    SelectReq   = 0x10,
    SelectAck   = 0x11,
    SelectNack  = 0x12,
    OperateReq  = 0x20,
    OperateAck  = 0x21,
    OperateNack = 0x22,
    CancelReq   = 0x30,
    CancelAck   = 0x31,
    StatusPing  = 0x40,
    StatusPong  = 0x41,
};

// --- Розділ 3: стани селектора ----------------------------------------
enum class State : std::uint8_t { Idle = 0x00, Armed = 0x01, Executing = 0x02 };

// --- Розділ 4: реєстр команд ------------------------------------------
enum class Cmd : std::uint16_t {
    None                = 0x0000,
    Ping                = 0x0001,
    RequestTelemetry    = 0x0002,
    EmergencyMotorCut   = 0x0101,
    ForceDisarm         = 0x0102,
    FlightModeOverride  = 0x0103,
    RebootAutopilot     = 0x0104,
    FactoryResetParams  = 0x0105,
    PayloadDropActuate  = 0x0106,
};

inline constexpr std::uint16_t kCriticalBase = 0x0100;

[[nodiscard]] constexpr bool is_critical(Cmd c) noexcept {
    return static_cast<std::uint16_t>(c) >= kCriticalBase;
}

// --- Розділ 5: коди відмов --------------------------------------------
enum class Error : std::uint8_t {
    Busy                = 0x01,
    InvalidToken        = 0x02,
    TimeoutExpired      = 0x03,
    NotArmed            = 0x04,
    CmdMismatch         = 0x05,
    BroadcastForbidden  = 0x06,
    HardwareFault       = 0x07,
};

// --- Розділ 6: часові параметри ---------------------------------------
inline constexpr Ms kArmMin{1000};
inline constexpr Ms kArmDefault{5000};
inline constexpr Ms kArmMax{15000};
inline constexpr Ms kAckWait{400};
inline constexpr Ms kCooldown{1000};
inline constexpr unsigned kRetries = 2;

// --- Розділ 8: прапорці у пакеті стану --------------------------------
inline constexpr std::uint8_t kFlagArmed = 0x01;
inline constexpr std::uint8_t kFlagLastReject = 0x02;

// --- Кадр --------------------------------------------------------------
struct Frame {
    std::uint8_t seq{};
    MsgType type{MsgType::StatusPing};
    std::uint8_t source{};
    std::uint8_t target{};
    Comp comp{Comp::Fc};
    State state{State::Idle};
    std::uint32_t token{};
    Cmd cmd{Cmd::None};
    Ms window{};
    std::vector<std::uint8_t> payload{};

    // Перший байт навантаження відповіді — код відмови розділу 5.
    [[nodiscard]] std::optional<Error> reason() const noexcept;
};

enum class DecodeError { TooShort, BadMagic, BadLength, BadCrc };

[[nodiscard]] constexpr std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (std::uint8_t byte : data) {
        crc ^= static_cast<std::uint16_t>(byte) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

// Кидає std::length_error, якщо навантаження не влазить у 128 байтів:
// це помилка виклику, а не стан дроту.
[[nodiscard]] std::vector<std::uint8_t> encode(const Frame& f);

[[nodiscard]] std::expected<Frame, DecodeError> decode(std::span<const std::uint8_t> raw);

[[nodiscard]] constexpr Ms clamp_window(Ms w) noexcept {
    if (w == Ms{0}) return kArmDefault;
    return std::clamp(w, kArmMin, kArmMax);
}

[[nodiscard]] std::string_view name(MsgType t) noexcept;
[[nodiscard]] std::string_view name(State s) noexcept;
[[nodiscard]] std::string_view name(Error e) noexcept;

}  // namespace sbo

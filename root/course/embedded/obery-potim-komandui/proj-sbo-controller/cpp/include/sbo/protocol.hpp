// protocol.hpp — кадр SBO у сильних типах: переплутати вузол із командою не вийде.
// Збірка: -std=c++23 (std::expected доступний у GCC 12); решта дизайну — C++20.
#pragma once

#include <array>
#include <chrono>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace sbo {

inline constexpr std::uint8_t  kMagic        = 0x5B;
inline constexpr std::uint8_t  kBroadcastId  = 0xFF;
inline constexpr std::uint8_t  kGcsDefaultId = 0xFE;
inline constexpr std::size_t   kHeaderLen    = 16;
inline constexpr std::size_t   kCrcLen       = 2;
inline constexpr std::size_t   kMaxPayload   = 64;
inline constexpr std::size_t   kMinFrameLen  = kHeaderLen + kCrcLen;
inline constexpr std::size_t   kMaxFrameLen  = kHeaderLen + kMaxPayload + kCrcLen;

inline constexpr std::chrono::milliseconds kDefaultWindow{5000};
inline constexpr std::chrono::milliseconds kMaxWindow{30000};

enum class State : std::uint8_t { Idle = 0, Armed = 1, Executing = 2 };

enum class MessageType : std::uint8_t {
    SelectReq   = 0x10,
    SelectAck   = 0x11,
    SelectNack  = 0x12,
    OperateReq  = 0x20,
    OperateAck  = 0x21,
    OperateNack = 0x22,
    CancelReq   = 0x30,
    CancelAck   = 0x31,
    CancelNack  = 0x32
};

enum class Error : std::uint8_t {
    Busy = 1,
    InvalidToken,
    TimeoutExpired,
    NotArmed,
    CommandMismatch,
    SourceMismatch,
    BroadcastForbidden,
    ForeignTarget,
    BadMagic,
    BadLength,
    BadCrc,
    UnknownType,
    InternalFault
};

// Сильні типи замість голих чисел: NodeId у поле CommandCode не підставиться.
struct NodeId {
    std::uint8_t value{0};
    constexpr NodeId() noexcept = default;
    constexpr explicit NodeId(std::uint8_t v) noexcept : value(v) {}
    [[nodiscard]] constexpr bool is_broadcast() const noexcept { return value == kBroadcastId; }
    constexpr auto operator<=>(const NodeId&) const noexcept = default;
};

struct Token {
    std::uint32_t value{0};
    constexpr Token() noexcept = default;
    constexpr explicit Token(std::uint32_t v) noexcept : value(v) {}
    [[nodiscard]] constexpr bool valid() const noexcept { return value != 0; }
    constexpr auto operator<=>(const Token&) const noexcept = default;
};

struct CommandCode {
    std::uint16_t value{0};
    constexpr CommandCode() noexcept = default;
    constexpr explicit CommandCode(std::uint16_t v) noexcept : value(v) {}
    constexpr auto operator<=>(const CommandCode&) const noexcept = default;
};

// Розібраний кадр. std::array замість вказівника з довжиною — купа не потрібна.
struct Frame {
    NodeId       source{};
    NodeId       target{};
    std::uint8_t component{0};
    std::uint8_t seq{0};
    MessageType  type{MessageType::SelectReq};
    State        state{State::Idle};
    Token        token{};
    CommandCode  command{};
    std::chrono::milliseconds timeout{0};
    std::array<std::uint8_t, kMaxPayload> payload{};
    std::uint8_t payload_len{0};

    [[nodiscard]] std::span<const std::uint8_t> data() const noexcept {
        return std::span{payload.data(), payload_len};
    }
    void set_data(std::span<const std::uint8_t> in) noexcept;
};

[[nodiscard]] std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept;

// Повертає ЗАПОВНЕНУ частину буфера — довжина й дані нероздільні.
[[nodiscard]] std::expected<std::span<std::uint8_t>, Error>
encode(const Frame& frame, std::span<std::uint8_t> out) noexcept;

[[nodiscard]] std::expected<Frame, Error> decode(std::span<const std::uint8_t> wire) noexcept;

[[nodiscard]] std::string_view to_string(Error err) noexcept;

}  // namespace sbo

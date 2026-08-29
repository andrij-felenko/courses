#pragma once

// Дротовий формат команди й квитанції — той самий, що в C-версії.
//
// Кадр команди (little-endian):
//    0  4  magic "CMD1" · 4  1  version · 5  1  type · 6  4  seq
//   10  8  token · 18  4  ttl_ms · 22  1  payload_len · 23 .. payload · +4 crc32
// Кадр квитанції (27 байтів): magic "ACK1", version, phase, state, token,
// result, detail, crc32.
//
// Розбір повертає std::expected: помилка кадру — це не виняткова ситуація,
// а звичайний робочий результат прийому з ефіру, і викликач мусить її
// обробити, а не проґавити забутою перевіркою -1.

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

#include "clock.hpp"

namespace cmdctl {

inline constexpr std::uint32_t MagicCommand = 0x434D4431u;  // "CMD1"
inline constexpr std::uint32_t MagicAck     = 0x41434B31u;  // "ACK1"
inline constexpr std::uint8_t  WireVersion  = 1;

inline constexpr std::size_t CommandHeader = 23;
inline constexpr std::size_t MaxPayload    = 16;
inline constexpr std::size_t MaxFrame      = CommandHeader + MaxPayload + 4;
inline constexpr std::size_t AckFrameSize  = 27;

enum class Type : std::uint8_t {
    Noop       = 0,
    SetRelay   = 1,   // payload: u8 канал, u8 стан
    GotoPos    = 2,   // payload: i32 абсолютна позиція
    DispenseMl = 3,   // payload: u16 мілілітри (неідемпотентна дія)
    Calibrate  = 4
};

enum class State : std::uint8_t { Free, Accepted, Executing, Succeeded, Failed, Expired };

enum class Error : std::int32_t {
    Ok = 0,
    ShortFrame = -1, BadMagic = -2, BadVersion = -3, BadCrc = -4, BadLength = -5,
    Replay = -6, Expired = -7, Superseded = -8, NoSlot = -9, QueueFull = -10,
    UnknownType = -11, BadPayload = -12, SupplySag = -13, Stall = -14, PowerReset = -15
};

struct Command {
    Type          type{Type::Noop};
    std::uint64_t token{0};
    std::uint32_t seq{0};
    Millis        ttl{0};
    std::array<std::byte, MaxPayload> payload{};
    std::uint8_t  payload_len{0};

    [[nodiscard]] std::span<const std::byte> data() const noexcept {
        return std::span{payload}.first(payload_len);
    }
};

struct Ack {
    std::uint64_t token{0};
    std::uint8_t  phase{1};
    State         state{State::Accepted};
    Error         result{Error::Ok};
    std::int32_t  detail{0};
};

// Кадр у стеку: купа в прошивці не потрібна, а розмір відомий наперед.
struct Frame {
    std::array<std::byte, MaxFrame> bytes{};
    std::size_t size{0};

    [[nodiscard]] std::span<const std::byte> view() const noexcept {
        return std::span{bytes}.first(size);
    }
};

[[nodiscard]] std::uint32_t crc32(std::span<const std::byte> data) noexcept;

[[nodiscard]] std::expected<Command, Error> parse_command(std::span<const std::byte> in) noexcept;
[[nodiscard]] Frame encode_command(const Command& cmd) noexcept;
[[nodiscard]] Frame encode_ack(const Ack& ack) noexcept;
[[nodiscard]] std::optional<Ack> parse_ack(std::span<const std::byte> in) noexcept;

// Робота з корисним навантаженням — теж через span, без голих покажчиків.
void put_u16(std::span<std::byte> out, std::uint16_t v) noexcept;
void put_i32(std::span<std::byte> out, std::int32_t v) noexcept;
[[nodiscard]] std::optional<std::uint16_t> get_u16(std::span<const std::byte> in) noexcept;
[[nodiscard]] std::optional<std::int32_t>  get_i32(std::span<const std::byte> in) noexcept;

[[nodiscard]] std::string_view name(Type type) noexcept;
[[nodiscard]] std::string_view name(State state) noexcept;
[[nodiscard]] std::string_view name(Error err) noexcept;

}  // namespace cmdctl

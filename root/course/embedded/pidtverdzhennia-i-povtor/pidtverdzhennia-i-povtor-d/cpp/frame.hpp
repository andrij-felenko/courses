// frame.hpp — кадр Stop-and-Wait ARQ і його кодек.
//
// Кадр на лінії:
//   SOF | TYPE | SEQ | LEN | PAYLOAD[LEN] | CRC16 (little-endian)
// Помилки розбору повертаємо як std::expected: у протокольному коді
// «зіпсований кадр» — звичайна очікувана подія, а не виняткова ситуація.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace arq {

inline constexpr std::uint8_t kSof = 0x7E;
inline constexpr std::size_t  kMaxPayload = 64;
inline constexpr std::size_t  kHeaderLen  = 4; // SOF | TYPE | SEQ | LEN
inline constexpr std::size_t  kCrcLen     = 2;
inline constexpr std::size_t  kMaxFrame   = kHeaderLen + kMaxPayload + kCrcLen;
inline constexpr std::size_t  kCtrlFrame  = kHeaderLen + kCrcLen;

inline constexpr unsigned kMaxRetries = 5;

enum class Type : std::uint8_t {
    Data = 0x01,
    Ack  = 0x02,
    Nack = 0x03,
};

enum class DecodeError : std::uint8_t { TooShort, NoSof, BadLength, BadType, BadSeq, BadCrc };
enum class EncodeError : std::uint8_t { PayloadTooBig, BufferTooSmall };

[[nodiscard]] std::string_view describe(DecodeError error) noexcept;

class Frame {
public:
    Frame() = default;

    // Фабрика замість кидучого конструктора: завелике навантаження це
    // помилка виклику, а не привід тягти винятки у драйвер лінії.
    [[nodiscard]] static std::expected<Frame, EncodeError>
    make(Type type, std::uint8_t seq, std::span<const std::uint8_t> payload) noexcept;

    [[nodiscard]] Type type() const noexcept { return type_; }
    [[nodiscard]] std::uint8_t seq() const noexcept { return seq_; }
    [[nodiscard]] std::span<const std::uint8_t> payload() const noexcept {
        return std::span<const std::uint8_t>{buffer_.data(), len_};
    }

private:
    Type         type_{Type::Data};
    std::uint8_t seq_{0};
    std::uint8_t len_{0};
    std::array<std::uint8_t, kMaxPayload> buffer_{};
};

[[nodiscard]] std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept;

// Пакує кадр у наданий буфер і повертає підспан із реальною довжиною —
// жодної купи, буфер завжди належить викликачеві.
[[nodiscard]] std::expected<std::span<const std::uint8_t>, EncodeError>
encode(const Frame& frame, std::span<std::uint8_t> out) noexcept;

[[nodiscard]] std::expected<Frame, DecodeError>
decode(std::span<const std::uint8_t> wire) noexcept;

} // namespace arq

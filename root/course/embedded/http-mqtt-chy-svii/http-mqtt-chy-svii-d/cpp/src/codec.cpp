// codec.cpp — вся робота з байтами кадру.
//
// Жодного reinterpret_cast: перехід «структура ↔ 16 байтів» робить
// std::bit_cast, і компілятор сам стежить, щоб розміри збігалися.
#include "codec.hpp"

#include <algorithm>
#include <array>
#include <bit>

namespace telemetry {

namespace {
using RawFrame = std::array<std::byte, kTelemetrySize>;

// CRC рахуємо по всьому кадру, крім самого поля crc (останні два байти).
constexpr std::size_t kCrcCovered = kTelemetrySize - sizeof(std::uint16_t);
}  // namespace

// CRC-16-CCITT: поліном 0x1021, початкове значення 0xFFFF.
// Побітовий варіант — нуль байтів таблиці в RAM, вісім ітерацій на байт.
std::uint16_t crc16(std::span<const std::byte> data) noexcept
{
    std::uint16_t crc = 0xFFFF;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) != 0
                      ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                      : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::expected<std::span<const std::byte>, FrameError>
encodeTelemetry(const Sample& sample, std::uint16_t seq,
                std::span<std::byte> out) noexcept
{
    if (out.size() < kTelemetrySize) {
        return std::unexpected(FrameError::BufferTooSmall);
    }

    Packet packet{};
    packet.magic       = kMagic;
    packet.type        = static_cast<std::uint8_t>(MsgType::Telemetry);
    packet.seq         = seq;
    packet.timestamp   = sample.timestamp;
    packet.temperature = sample.temperature;
    packet.humidity    = sample.humidity;
    packet.vbat_mv     = sample.vbat_mv;
    packet.crc         = 0;

    // Байтове представлення потрібне двічі: спершу щоб порахувати CRC,
    // потім — щоб віддати вже повний кадр.
    auto bytes = std::bit_cast<RawFrame>(packet);
    packet.crc = crc16(std::span<const std::byte>{bytes}.first(kCrcCovered));
    bytes = std::bit_cast<RawFrame>(packet);

    std::ranges::copy(bytes, out.begin());
    return out.first(kTelemetrySize);
}

std::expected<Packet, FrameError>
decodeTelemetry(std::span<const std::byte> raw) noexcept
{
    if (raw.size() < kTelemetrySize) {
        return std::unexpected(FrameError::TooShort);
    }

    // Копіюємо у власний масив: буфер прийому не зобов'язаний лежати
    // з вирівнюванням, потрібним структурі.
    RawFrame bytes{};
    std::ranges::copy(raw.first(kTelemetrySize), bytes.begin());
    const auto packet = std::bit_cast<Packet>(bytes);

    if (packet.magic != kMagic) {
        return std::unexpected(FrameError::BadMagic);
    }
    if (packet.type != static_cast<std::uint8_t>(MsgType::Telemetry)) {
        return std::unexpected(FrameError::BadType);
    }
    if (crc16(std::span<const std::byte>{bytes}.first(kCrcCovered)) != packet.crc) {
        return std::unexpected(FrameError::BadCrc);
    }
    return packet;
}

// Підтвердження — чотири байти: магія, тип, номер кадру.
// CRC тут зайвий: єдине змістовне поле — seq, а хибний seq просто не збігається
// з очікуваним і відкидається тією самою перевіркою.
std::expected<std::span<const std::byte>, FrameError>
encodeAck(std::uint16_t seq, std::span<std::byte> out) noexcept
{
    if (out.size() < kAckSize) {
        return std::unexpected(FrameError::BufferTooSmall);
    }
    out[0] = std::byte{kMagic};
    out[1] = static_cast<std::byte>(MsgType::Ack);
    out[2] = static_cast<std::byte>(seq & 0xFF);
    out[3] = static_cast<std::byte>(seq >> 8);
    return out.first(kAckSize);
}

std::expected<std::uint16_t, FrameError>
decodeAck(std::span<const std::byte> raw) noexcept
{
    if (raw.size() < kAckSize) {
        return std::unexpected(FrameError::TooShort);
    }
    if (raw[0] != std::byte{kMagic}) {
        return std::unexpected(FrameError::BadMagic);
    }
    if (raw[1] != static_cast<std::byte>(MsgType::Ack)) {
        return std::unexpected(FrameError::BadType);
    }
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(raw[2]) |
                                      (std::to_integer<std::uint16_t>(raw[3]) << 8));
}

std::string_view describe(FrameError error) noexcept
{
    switch (error) {
    case FrameError::TooShort:       return "датаграма коротша за кадр";
    case FrameError::BadMagic:       return "чужа магія";
    case FrameError::BadType:        return "не той тип повідомлення";
    case FrameError::BadCrc:         return "не збігся CRC";
    case FrameError::BufferTooSmall: return "замалий буфер";
    }
    return "невідома помилка";
}

}  // namespace telemetry

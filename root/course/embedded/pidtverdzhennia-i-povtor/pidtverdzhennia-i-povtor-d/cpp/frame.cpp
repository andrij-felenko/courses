#include "frame.hpp"

#include <algorithm>
#include <utility>

namespace arq {
namespace {

constexpr std::uint16_t kPoly = 0x1021; // CRC-16/CCITT-FALSE

} // namespace

std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept
{
    std::uint16_t crc = 0xFFFF;
    for (const std::uint8_t byte : data) {
        crc ^= static_cast<std::uint16_t>(static_cast<std::uint16_t>(byte) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ kPoly)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::expected<Frame, EncodeError>
Frame::make(Type type, std::uint8_t seq, std::span<const std::uint8_t> payload) noexcept
{
    if (payload.size() > kMaxPayload) {
        return std::unexpected(EncodeError::PayloadTooBig);
    }
    Frame frame;
    frame.type_ = type;
    frame.seq_  = static_cast<std::uint8_t>(seq & 1u); // однобітний номер
    frame.len_  = static_cast<std::uint8_t>(payload.size());
    std::ranges::copy(payload, frame.buffer_.begin());
    return frame;
}

std::expected<std::span<const std::uint8_t>, EncodeError>
encode(const Frame& frame, std::span<std::uint8_t> out) noexcept
{
    const auto payload = frame.payload();
    const std::size_t total = kHeaderLen + payload.size() + kCrcLen;
    if (out.size() < total) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }

    out[0] = kSof;
    out[1] = std::to_underlying(frame.type());
    out[2] = frame.seq();
    out[3] = static_cast<std::uint8_t>(payload.size());
    std::ranges::copy(payload, out.begin() + static_cast<std::ptrdiff_t>(kHeaderLen));

    // CRC накриває все, крім самого SOF: маркер синхронізації не є даними.
    const std::uint16_t crc = crc16(out.subspan(1, 3 + payload.size()));
    out[total - 2] = static_cast<std::uint8_t>(crc & 0xFF);
    out[total - 1] = static_cast<std::uint8_t>(crc >> 8);
    return out.subspan(0, total);
}

std::expected<Frame, DecodeError> decode(std::span<const std::uint8_t> wire) noexcept
{
    if (wire.size() < kHeaderLen + kCrcLen) {
        return std::unexpected(DecodeError::TooShort);
    }
    if (wire[0] != kSof) {
        return std::unexpected(DecodeError::NoSof);
    }

    const std::size_t len = wire[3];
    if (len > kMaxPayload || wire.size() != kHeaderLen + len + kCrcLen) {
        return std::unexpected(DecodeError::BadLength);
    }

    // Спершу CRC — далі полям заголовка вже можна вірити.
    const auto expectedCrc = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(wire[wire.size() - 2]) |
        static_cast<std::uint16_t>(static_cast<std::uint16_t>(wire[wire.size() - 1]) << 8));
    if (crc16(wire.subspan(1, 3 + len)) != expectedCrc) {
        return std::unexpected(DecodeError::BadCrc);
    }

    const auto type = static_cast<Type>(wire[1]);
    if (type != Type::Data && type != Type::Ack && type != Type::Nack) {
        return std::unexpected(DecodeError::BadType);
    }
    if (type != Type::Data && len != 0) {
        return std::unexpected(DecodeError::BadLength); // квитанція з даними — не наш протокол
    }
    if (wire[2] > 1) {
        return std::unexpected(DecodeError::BadSeq); // у Stop-and-Wait номер однобітний
    }

    auto frame = Frame::make(type, wire[2], wire.subspan(kHeaderLen, len));
    if (!frame) {
        return std::unexpected(DecodeError::BadLength);
    }
    return *frame;
}

std::string_view describe(DecodeError error) noexcept
{
    switch (error) {
    case DecodeError::TooShort:  return "закороткий кадр";
    case DecodeError::NoSof:     return "немає SOF";
    case DecodeError::BadLength: return "невірна довжина";
    case DecodeError::BadType:   return "невідомий тип";
    case DecodeError::BadSeq:    return "номер поза 0/1";
    case DecodeError::BadCrc:    return "CRC не збігся";
    }
    return "?";
}

} // namespace arq

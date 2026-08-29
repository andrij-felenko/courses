// protocol.cpp — CRC, серіалізація й валідатор кадру.
#include "sbo/protocol.hpp"

#include <algorithm>

namespace sbo {
namespace {

void put_u16(std::span<std::uint8_t> out, std::size_t at, std::uint16_t v) noexcept {
    out[at]     = static_cast<std::uint8_t>(v & 0xFFu);
    out[at + 1] = static_cast<std::uint8_t>(v >> 8);
}

void put_u32(std::span<std::uint8_t> out, std::size_t at, std::uint32_t v) noexcept {
    out[at]     = static_cast<std::uint8_t>(v & 0xFFu);
    out[at + 1] = static_cast<std::uint8_t>((v >> 8) & 0xFFu);
    out[at + 2] = static_cast<std::uint8_t>((v >> 16) & 0xFFu);
    out[at + 3] = static_cast<std::uint8_t>((v >> 24) & 0xFFu);
}

[[nodiscard]] std::uint16_t get_u16(std::span<const std::uint8_t> in, std::size_t at) noexcept {
    return static_cast<std::uint16_t>(in[at] | (static_cast<std::uint16_t>(in[at + 1]) << 8));
}

[[nodiscard]] std::uint32_t get_u32(std::span<const std::uint8_t> in, std::size_t at) noexcept {
    return static_cast<std::uint32_t>(in[at]) |
           (static_cast<std::uint32_t>(in[at + 1]) << 8) |
           (static_cast<std::uint32_t>(in[at + 2]) << 16) |
           (static_cast<std::uint32_t>(in[at + 3]) << 24);
}

[[nodiscard]] std::expected<MessageType, Error> parse_type(std::uint8_t raw) noexcept {
    switch (raw) {
    case 0x10: return MessageType::SelectReq;
    case 0x11: return MessageType::SelectAck;
    case 0x12: return MessageType::SelectNack;
    case 0x20: return MessageType::OperateReq;
    case 0x21: return MessageType::OperateAck;
    case 0x22: return MessageType::OperateNack;
    case 0x30: return MessageType::CancelReq;
    case 0x31: return MessageType::CancelAck;
    case 0x32: return MessageType::CancelNack;
    default:   return std::unexpected(Error::UnknownType);
    }
}

}  // namespace

void Frame::set_data(std::span<const std::uint8_t> in) noexcept {
    const std::size_t n = std::min(in.size(), kMaxPayload);
    std::copy_n(in.begin(), n, payload.begin());
    payload_len = static_cast<std::uint8_t>(n);
}

std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept {
    std::uint16_t crc = 0xFFFFu;   // CRC-16/CCITT-FALSE, поліном 0x1021
    for (const std::uint8_t byte : data) {
        crc ^= static_cast<std::uint16_t>(static_cast<std::uint16_t>(byte) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021u)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::expected<std::span<std::uint8_t>, Error> encode(const Frame& frame,
                                                     std::span<std::uint8_t> out) noexcept {
    if (frame.payload_len > kMaxPayload) {
        return std::unexpected(Error::BadLength);
    }
    const std::size_t body  = kHeaderLen + frame.payload_len;
    const std::size_t total = body + kCrcLen;
    if (out.size() < total) {
        return std::unexpected(Error::BadLength);
    }

    const auto window = std::clamp<std::int64_t>(frame.timeout.count(), 0, 0xFFFF);

    out[0] = kMagic;
    out[1] = frame.payload_len;
    out[2] = frame.seq;
    out[3] = static_cast<std::uint8_t>(frame.type);
    out[4] = frame.source.value;
    out[5] = frame.target.value;
    out[6] = frame.component;
    out[7] = static_cast<std::uint8_t>(frame.state);
    put_u32(out, 8, frame.token.value);
    put_u16(out, 12, frame.command.value);
    put_u16(out, 14, static_cast<std::uint16_t>(window));
    std::copy_n(frame.payload.begin(), frame.payload_len, out.begin() + kHeaderLen);
    put_u16(out, body, crc16(out.first(body)));

    return out.first(total);
}

std::expected<Frame, Error> decode(std::span<const std::uint8_t> wire) noexcept {
    if (wire.size() < kMinFrameLen || wire.size() > kMaxFrameLen) {
        return std::unexpected(Error::BadLength);
    }
    if (wire[0] != kMagic) {
        return std::unexpected(Error::BadMagic);
    }
    const std::uint8_t payload_len = wire[1];
    if (payload_len > kMaxPayload) {
        return std::unexpected(Error::BadLength);
    }
    const std::size_t body = kHeaderLen + payload_len;
    if (wire.size() != body + kCrcLen) {
        return std::unexpected(Error::BadLength);
    }
    if (get_u16(wire, body) != crc16(wire.first(body))) {
        return std::unexpected(Error::BadCrc);
    }
    const auto type = parse_type(wire[3]);
    if (!type) {
        return std::unexpected(type.error());
    }

    Frame frame{};
    frame.seq       = wire[2];
    frame.type      = *type;
    frame.source    = NodeId{wire[4]};
    frame.target    = NodeId{wire[5]};
    frame.component = wire[6];
    frame.state     = static_cast<State>(std::min<std::uint8_t>(wire[7], 2));
    frame.token     = Token{get_u32(wire, 8)};
    frame.command   = CommandCode{get_u16(wire, 12)};
    frame.timeout   = std::chrono::milliseconds{get_u16(wire, 14)};
    frame.set_data(wire.subspan(kHeaderLen, payload_len));
    return frame;
}

std::string_view to_string(Error err) noexcept {
    using enum Error;
    switch (err) {
    case Busy:               return "зайнято іншим оператором";
    case InvalidToken:       return "недійсний токен";
    case TimeoutExpired:     return "вікно селекції спливло";
    case NotArmed:           return "замок не зведено";
    case CommandMismatch:    return "команда не та, що вибиралася";
    case SourceMismatch:     return "токен з чужої адреси";
    case BroadcastForbidden: return "широкомовна критична дія заборонена";
    case ForeignTarget:      return "кадр адресовано іншому вузлу";
    case BadMagic:           return "чужий кадр (magic)";
    case BadLength:          return "неправильна довжина кадру";
    case BadCrc:             return "CRC не збігся";
    case UnknownType:        return "невідомий тип повідомлення";
    default:                 return "внутрішня помилка";
    }
}

}  // namespace sbo

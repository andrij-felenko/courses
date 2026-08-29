#include "protocol.hpp"

#include <algorithm>
#include <iterator>
#include <stdexcept>
#include <utility>

namespace sbo {
namespace {

void put16(std::vector<std::uint8_t>& out, std::uint16_t v) {
    out.push_back(static_cast<std::uint8_t>(v & 0xFF));
    out.push_back(static_cast<std::uint8_t>(v >> 8));
}

void put32(std::vector<std::uint8_t>& out, std::uint32_t v) {
    out.push_back(static_cast<std::uint8_t>(v & 0xFF));
    out.push_back(static_cast<std::uint8_t>((v >> 8) & 0xFF));
    out.push_back(static_cast<std::uint8_t>((v >> 16) & 0xFF));
    out.push_back(static_cast<std::uint8_t>((v >> 24) & 0xFF));
}

std::uint16_t get16(std::span<const std::uint8_t> p) {
    return static_cast<std::uint16_t>(p[0] | (p[1] << 8));
}

std::uint32_t get32(std::span<const std::uint8_t> p) {
    return static_cast<std::uint32_t>(p[0]) |
           (static_cast<std::uint32_t>(p[1]) << 8) |
           (static_cast<std::uint32_t>(p[2]) << 16) |
           (static_cast<std::uint32_t>(p[3]) << 24);
}

}  // namespace

std::optional<Error> Frame::reason() const noexcept {
    if (payload.empty()) return std::nullopt;
    return static_cast<Error>(payload.front());
}

std::vector<std::uint8_t> encode(const Frame& f) {
    if (f.payload.size() > kMaxPayload) {
        throw std::length_error("SBO: навантаження понад 128 байтів");
    }

    std::vector<std::uint8_t> out;
    out.reserve(kHeaderLen + f.payload.size() + kCrcLen);
    out.push_back(kMagic);
    out.push_back(static_cast<std::uint8_t>(f.payload.size()));
    out.push_back(f.seq);
    out.push_back(std::to_underlying(f.type));
    out.push_back(f.source);
    out.push_back(f.target);
    out.push_back(std::to_underlying(f.comp));
    out.push_back(std::to_underlying(f.state));
    put32(out, f.token);
    put16(out, std::to_underlying(f.cmd));
    put16(out, static_cast<std::uint16_t>(f.window.count()));
    std::ranges::copy(f.payload, std::back_inserter(out));

    // Сума охоплює все зібране: від magic до кінця payload.
    put16(out, crc16(out));
    return out;
}

std::expected<Frame, DecodeError> decode(std::span<const std::uint8_t> raw) {
    if (raw.size() < kHeaderLen + kCrcLen) {
        return std::unexpected(DecodeError::TooShort);
    }
    if (raw[0] != kMagic) {
        return std::unexpected(DecodeError::BadMagic);
    }

    const std::size_t n = raw[1];
    if (n > kMaxPayload) {
        return std::unexpected(DecodeError::BadLength);
    }
    const std::size_t body = kHeaderLen + n;
    const std::size_t total = body + kCrcLen;
    if (raw.size() < total) {
        return std::unexpected(DecodeError::TooShort);
    }
    if (raw.size() > total) {
        // Хвіст після суми: злиплі кадри або сміття в ефірі.
        return std::unexpected(DecodeError::BadLength);
    }
    if (get16(raw.subspan(body)) != crc16(raw.first(body))) {
        return std::unexpected(DecodeError::BadCrc);
    }

    Frame f;
    f.seq = raw[2];
    f.type = static_cast<MsgType>(raw[3]);
    f.source = raw[4];
    f.target = raw[5];
    f.comp = static_cast<Comp>(raw[6]);
    f.state = static_cast<State>(raw[7]);
    f.token = get32(raw.subspan(8, 4));
    f.cmd = static_cast<Cmd>(get16(raw.subspan(12, 2)));
    f.window = Ms{get16(raw.subspan(14, 2))};
    f.payload.assign(raw.begin() + kHeaderLen, raw.begin() + body);
    return f;
}

std::string_view name(MsgType t) noexcept {
    switch (t) {
        case MsgType::SelectReq:   return "SELECT_REQ";
        case MsgType::SelectAck:   return "SELECT_ACK";
        case MsgType::SelectNack:  return "SELECT_NACK";
        case MsgType::OperateReq:  return "OPERATE_REQ";
        case MsgType::OperateAck:  return "OPERATE_ACK";
        case MsgType::OperateNack: return "OPERATE_NACK";
        case MsgType::CancelReq:   return "CANCEL_REQ";
        case MsgType::CancelAck:   return "CANCEL_ACK";
        case MsgType::StatusPing:  return "STATUS_PING";
        case MsgType::StatusPong:  return "STATUS_PONG";
    }
    return "UNKNOWN";
}

std::string_view name(State s) noexcept {
    switch (s) {
        case State::Idle:      return "IDLE";
        case State::Armed:     return "ARMED";
        case State::Executing: return "EXECUTING";
    }
    return "?";
}

std::string_view name(Error e) noexcept {
    switch (e) {
        case Error::Busy:               return "ERR_SBO_BUSY";
        case Error::InvalidToken:       return "ERR_SBO_INVALID_TOKEN";
        case Error::TimeoutExpired:     return "ERR_SBO_TIMEOUT_EXPIRED";
        case Error::NotArmed:           return "ERR_SBO_NOT_ARMED";
        case Error::CmdMismatch:        return "ERR_SBO_CMD_MISMATCH";
        case Error::BroadcastForbidden: return "ERR_SBO_BROADCAST_FORBIDDEN";
        case Error::HardwareFault:      return "ERR_SBO_HARDWARE_FAULT";
    }
    return "ERR_UNKNOWN";
}

}  // namespace sbo

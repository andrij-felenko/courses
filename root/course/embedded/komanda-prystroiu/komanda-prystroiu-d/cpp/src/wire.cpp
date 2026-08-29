#include "wire.hpp"

#include <algorithm>

namespace cmdctl {
namespace {

constexpr std::size_t OffMagic = 0, OffVer = 4, OffType = 5, OffSeq = 6;
constexpr std::size_t OffToken = 10, OffTtl = 18, OffPlen = 22;

constexpr std::size_t AOffMagic = 0, AOffVer = 4, AOffPhase = 5, AOffState = 6;
constexpr std::size_t AOffToken = 7, AOffResult = 15, AOffDetail = 19, AOffCrc = 23;

void put32(std::byte* p, std::uint32_t v) noexcept {
    p[0] = static_cast<std::byte>(v & 0xFFu);
    p[1] = static_cast<std::byte>((v >> 8) & 0xFFu);
    p[2] = static_cast<std::byte>((v >> 16) & 0xFFu);
    p[3] = static_cast<std::byte>((v >> 24) & 0xFFu);
}

[[nodiscard]] std::uint32_t get32(const std::byte* p) noexcept {
    return std::to_integer<std::uint32_t>(p[0]) |
           (std::to_integer<std::uint32_t>(p[1]) << 8) |
           (std::to_integer<std::uint32_t>(p[2]) << 16) |
           (std::to_integer<std::uint32_t>(p[3]) << 24);
}

void put64(std::byte* p, std::uint64_t v) noexcept {
    put32(p, static_cast<std::uint32_t>(v & 0xFFFFFFFFu));
    put32(p + 4, static_cast<std::uint32_t>(v >> 32));
}

[[nodiscard]] std::uint64_t get64(const std::byte* p) noexcept {
    return static_cast<std::uint64_t>(get32(p)) |
           (static_cast<std::uint64_t>(get32(p + 4)) << 32);
}

}  // namespace

std::uint32_t crc32(std::span<const std::byte> data) noexcept {
    std::uint32_t crc = 0xFFFFFFFFu;
    for (std::byte b : data) {
        crc ^= std::to_integer<std::uint32_t>(b);
        for (int i = 0; i < 8; ++i) {
            const std::uint32_t mask = ~(crc & 1u) + 1u;   // 0xFFFFFFFF, якщо біт стоїть
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

std::expected<Command, Error> parse_command(std::span<const std::byte> in) noexcept {
    if (in.size() < CommandHeader + 4) return std::unexpected(Error::ShortFrame);
    if (get32(in.data() + OffMagic) != MagicCommand) return std::unexpected(Error::BadMagic);
    if (std::to_integer<std::uint8_t>(in[OffVer]) != WireVersion) return std::unexpected(Error::BadVersion);

    const auto plen = std::to_integer<std::uint8_t>(in[OffPlen]);
    if (plen > MaxPayload) return std::unexpected(Error::BadLength);

    const std::size_t total = CommandHeader + plen + 4;
    if (in.size() < total) return std::unexpected(Error::ShortFrame);
    if (crc32(in.first(total - 4)) != get32(in.data() + total - 4)) return std::unexpected(Error::BadCrc);

    Command cmd;
    cmd.type        = static_cast<Type>(std::to_integer<std::uint8_t>(in[OffType]));
    cmd.seq         = get32(in.data() + OffSeq);
    cmd.token       = get64(in.data() + OffToken);
    cmd.ttl         = Millis{get32(in.data() + OffTtl)};
    cmd.payload_len = plen;
    std::copy_n(in.begin() + static_cast<std::ptrdiff_t>(CommandHeader), plen, cmd.payload.begin());
    return cmd;
}

Frame encode_command(const Command& cmd) noexcept {
    Frame f;
    const std::size_t plen = std::min<std::size_t>(cmd.payload_len, MaxPayload);
    f.size = CommandHeader + plen + 4;

    std::byte* p = f.bytes.data();
    put32(p + OffMagic, MagicCommand);
    p[OffVer]  = static_cast<std::byte>(WireVersion);
    p[OffType] = static_cast<std::byte>(cmd.type);
    put32(p + OffSeq, cmd.seq);
    put64(p + OffToken, cmd.token);
    put32(p + OffTtl, static_cast<std::uint32_t>(cmd.ttl.count()));
    p[OffPlen] = static_cast<std::byte>(plen);
    std::copy_n(cmd.payload.begin(), plen, f.bytes.begin() + static_cast<std::ptrdiff_t>(CommandHeader));

    put32(p + f.size - 4, crc32(f.view().first(f.size - 4)));
    return f;
}

Frame encode_ack(const Ack& ack) noexcept {
    Frame f;
    f.size = AckFrameSize;

    std::byte* p = f.bytes.data();
    put32(p + AOffMagic, MagicAck);
    p[AOffVer]   = static_cast<std::byte>(WireVersion);
    p[AOffPhase] = static_cast<std::byte>(ack.phase);
    p[AOffState] = static_cast<std::byte>(ack.state);
    put64(p + AOffToken, ack.token);
    put32(p + AOffResult, static_cast<std::uint32_t>(static_cast<std::int32_t>(ack.result)));
    put32(p + AOffDetail, static_cast<std::uint32_t>(ack.detail));
    put32(p + AOffCrc, crc32(f.view().first(AOffCrc)));
    return f;
}

std::optional<Ack> parse_ack(std::span<const std::byte> in) noexcept {
    if (in.size() < AckFrameSize) return std::nullopt;
    if (get32(in.data() + AOffMagic) != MagicAck) return std::nullopt;
    if (std::to_integer<std::uint8_t>(in[AOffVer]) != WireVersion) return std::nullopt;
    if (crc32(in.first(AOffCrc)) != get32(in.data() + AOffCrc)) return std::nullopt;

    Ack a;
    a.token  = get64(in.data() + AOffToken);
    a.phase  = std::to_integer<std::uint8_t>(in[AOffPhase]);
    a.state  = static_cast<State>(std::to_integer<std::uint8_t>(in[AOffState]));
    a.result = static_cast<Error>(static_cast<std::int32_t>(get32(in.data() + AOffResult)));
    a.detail = static_cast<std::int32_t>(get32(in.data() + AOffDetail));
    return a;
}

void put_u16(std::span<std::byte> out, std::uint16_t v) noexcept {
    if (out.size() < 2) return;
    out[0] = static_cast<std::byte>(v & 0xFFu);
    out[1] = static_cast<std::byte>((v >> 8) & 0xFFu);
}

void put_i32(std::span<std::byte> out, std::int32_t v) noexcept {
    if (out.size() < 4) return;
    put32(out.data(), static_cast<std::uint32_t>(v));
}

std::optional<std::uint16_t> get_u16(std::span<const std::byte> in) noexcept {
    if (in.size() < 2) return std::nullopt;
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(in[0]) |
                                      static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(in[1]) << 8));
}

std::optional<std::int32_t> get_i32(std::span<const std::byte> in) noexcept {
    if (in.size() < 4) return std::nullopt;
    return static_cast<std::int32_t>(get32(in.data()));
}

std::string_view name(Type type) noexcept {
    switch (type) {
        case Type::Noop:       return "NOOP";
        case Type::SetRelay:   return "SET_RELAY";
        case Type::GotoPos:    return "GOTO_POS";
        case Type::DispenseMl: return "DISPENSE_ML";
        case Type::Calibrate:  return "CALIBRATE";
    }
    return "?";
}

std::string_view name(State state) noexcept {
    switch (state) {
        case State::Free:      return "FREE";
        case State::Accepted:  return "ACCEPTED";
        case State::Executing: return "EXECUTING";
        case State::Succeeded: return "SUCCEEDED";
        case State::Failed:    return "FAILED";
        case State::Expired:   return "EXPIRED";
    }
    return "?";
}

std::string_view name(Error err) noexcept {
    switch (err) {
        case Error::Ok:          return "OK";
        case Error::ShortFrame:  return "SHORT_FRAME";
        case Error::BadMagic:    return "BAD_MAGIC";
        case Error::BadVersion:  return "BAD_VERSION";
        case Error::BadCrc:      return "BAD_CRC";
        case Error::BadLength:   return "BAD_LENGTH";
        case Error::Replay:      return "REPLAY";
        case Error::Expired:     return "EXPIRED";
        case Error::Superseded:  return "SUPERSEDED";
        case Error::NoSlot:      return "NO_SLOT";
        case Error::QueueFull:   return "QUEUE_FULL";
        case Error::UnknownType: return "UNKNOWN_TYPE";
        case Error::BadPayload:  return "BAD_PAYLOAD";
        case Error::SupplySag:   return "SUPPLY_SAG";
        case Error::Stall:       return "STALL";
        case Error::PowerReset:  return "POWER_RESET";
    }
    return "?";
}

}  // namespace cmdctl

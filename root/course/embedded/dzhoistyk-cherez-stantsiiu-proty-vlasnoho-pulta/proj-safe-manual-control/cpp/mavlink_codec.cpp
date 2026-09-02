#include "mavlink_codec.hpp"

#include <algorithm>
#include <cstring>

namespace mavlink {
namespace {

// CRC-16/MCRF4XX — той самий поліном, що в mavlink_helpers.h.
constexpr void crcAccumulate(std::uint16_t& crc, std::uint8_t b) noexcept
{
    std::uint8_t tmp = b ^ static_cast<std::uint8_t>(crc & 0xFFU);
    tmp = static_cast<std::uint8_t>(tmp ^ static_cast<std::uint8_t>(tmp << 4));
    crc = static_cast<std::uint16_t>((crc >> 8) ^ (static_cast<std::uint16_t>(tmp) << 8) ^
                                     (static_cast<std::uint16_t>(tmp) << 3) ^
                                     (static_cast<std::uint16_t>(tmp) >> 4));
}

struct MsgInfo {
    std::uint8_t crcExtra;
    std::uint8_t length;
};

// CRC_EXTRA і канонічні довжини — з XML діалекту common.
[[nodiscard]] std::optional<MsgInfo> msgInfo(std::uint32_t msgid) noexcept
{
    switch (msgid) {
    case kMsgHeartbeat:     return MsgInfo{50, 9};
    case kMsgManualControl: return MsgInfo{243, 11};
    case kMsgCommandLong:   return MsgInfo{152, 33};
    case kMsgCommandAck:    return MsgInfo{143, 3};
    default:                return std::nullopt;
    }
}

[[nodiscard]] std::uint16_t readU16(std::span<const std::byte> p, std::size_t at) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(p[at]) |
                                      (std::to_integer<std::uint16_t>(p[at + 1]) << 8));
}

[[nodiscard]] std::int16_t readI16(std::span<const std::byte> p, std::size_t at) noexcept
{
    return static_cast<std::int16_t>(readU16(p, at));
}

[[nodiscard]] std::uint32_t readU32(std::span<const std::byte> p, std::size_t at) noexcept
{
    return std::to_integer<std::uint32_t>(p[at]) |
           (std::to_integer<std::uint32_t>(p[at + 1]) << 8) |
           (std::to_integer<std::uint32_t>(p[at + 2]) << 16) |
           (std::to_integer<std::uint32_t>(p[at + 3]) << 24);
}

[[nodiscard]] float readF32(std::span<const std::byte> p, std::size_t at) noexcept
{
    const std::uint32_t bits = readU32(p, at);
    float f{};
    std::memcpy(&f, &bits, sizeof(f));
    return f;
}

void writeU16(std::span<std::byte> p, std::size_t at, std::uint16_t v) noexcept
{
    p[at]     = std::byte{static_cast<std::uint8_t>(v)};
    p[at + 1] = std::byte{static_cast<std::uint8_t>(v >> 8)};
}

void writeI16(std::span<std::byte> p, std::size_t at, std::int16_t v) noexcept
{
    writeU16(p, at, static_cast<std::uint16_t>(v));
}

void writeU32(std::span<std::byte> p, std::size_t at, std::uint32_t v) noexcept
{
    for (std::size_t i = 0; i < 4; ++i)
        p[at + i] = std::byte{static_cast<std::uint8_t>(v >> (8 * i))};
}

void writeF32(std::span<std::byte> p, std::size_t at, float f) noexcept
{
    std::uint32_t bits{};
    std::memcpy(&bits, &f, sizeof(bits));
    writeU32(p, at, bits);
}

template <class... Ts>
struct Overloaded : Ts... { using Ts::operator()...; };
template <class... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;

}  // namespace

void Parser::enterPayload() noexcept
{
    idx_ = 0;
    payload_.fill(std::byte{0});  // тут же відновлюються обрізані нулі v2
    stage_ = (len_ == 0) ? Stage::Crc1 : Stage::Payload;
}

std::optional<Frame> Parser::push(std::byte b) noexcept
{
    if (skip_ > 0) {  // хвіст підпису кадру v2 — тіло вже віддано
        --skip_;
        return std::nullopt;
    }

    const auto raw = std::to_integer<std::uint8_t>(b);

    switch (stage_) {
    case Stage::Idle:
        if (b == kStxV2 || b == kStxV1) {
            isV2_     = (b == kStxV2);
            crc_      = 0xFFFFU;
            incompat_ = 0;
            stage_    = Stage::Len;
        }
        return std::nullopt;

    case Stage::Len:
        len_ = raw;
        crcAccumulate(crc_, raw);
        stage_ = isV2_ ? Stage::Incompat : Stage::Seq;
        return std::nullopt;

    case Stage::Incompat:
        incompat_ = raw;
        crcAccumulate(crc_, raw);
        // 0x01 — підпис, його вміємо пропустити. Будь-який інший прапорець
        // означає кадр, якого ми не розуміємо: специфікація велить відкинути.
        if ((raw & static_cast<std::uint8_t>(~0x01U)) != 0) {
            ++stats_.unsupported;
            stage_ = Stage::Idle;
            return std::nullopt;
        }
        stage_ = Stage::Compat;
        return std::nullopt;

    case Stage::Compat:
        crcAccumulate(crc_, raw);
        stage_ = Stage::Seq;
        return std::nullopt;

    case Stage::Seq:
        seq_ = raw;
        crcAccumulate(crc_, raw);
        stage_ = Stage::Sysid;
        return std::nullopt;

    case Stage::Sysid:
        sysid_ = raw;
        crcAccumulate(crc_, raw);
        stage_ = Stage::Compid;
        return std::nullopt;

    case Stage::Compid:
        compid_ = raw;
        crcAccumulate(crc_, raw);
        stage_ = Stage::Msgid1;
        return std::nullopt;

    case Stage::Msgid1:
        msgid_ = raw;
        crcAccumulate(crc_, raw);
        if (isV2_)
            stage_ = Stage::Msgid2;
        else
            enterPayload();  // у v1 ідентифікатор однобайтовий
        return std::nullopt;

    case Stage::Msgid2:
        msgid_ |= static_cast<std::uint32_t>(raw) << 8;
        crcAccumulate(crc_, raw);
        stage_ = Stage::Msgid3;
        return std::nullopt;

    case Stage::Msgid3:
        msgid_ |= static_cast<std::uint32_t>(raw) << 16;
        crcAccumulate(crc_, raw);
        enterPayload();
        return std::nullopt;

    case Stage::Payload:
        payload_[idx_++] = b;
        crcAccumulate(crc_, raw);
        if (idx_ >= len_)
            stage_ = Stage::Crc1;
        return std::nullopt;

    case Stage::Crc1:
        rxCrc_ = raw;
        stage_ = Stage::Crc2;
        return std::nullopt;

    case Stage::Crc2: {
        rxCrc_ |= static_cast<std::uint16_t>(raw) << 8;
        stage_ = Stage::Idle;
        if (isV2_ && (incompat_ & 0x01U) != 0)
            skip_ = static_cast<std::uint8_t>(kSignatureLen);

        const auto info = msgInfo(msgid_);
        if (!info) {  // без CRC_EXTRA кадр узагалі не перевірити
            ++stats_.unknown;
            return std::nullopt;
        }

        std::uint16_t crc = crc_;
        crcAccumulate(crc, info->crcExtra);
        if (crc != rxCrc_) {
            ++stats_.crcErrors;
            return std::nullopt;
        }

        Frame f{};
        f.sysid   = sysid_;
        f.compid  = compid_;
        f.seq     = seq_;
        f.msgid   = msgid_;
        f.len     = len_;
        f.payload = payload_;
        ++stats_.frames;
        return f;
    }
    }
    stage_ = Stage::Idle;
    return std::nullopt;
}

std::optional<Message> decode(const Frame& f) noexcept
{
    const std::span<const std::byte> p{f.payload};

    switch (f.msgid) {
    case kMsgHeartbeat: {
        Heartbeat hb{};
        hb.customMode     = readU32(p, 0);
        hb.type           = std::to_integer<std::uint8_t>(p[4]);
        hb.autopilot      = std::to_integer<std::uint8_t>(p[5]);
        hb.baseMode       = std::to_integer<std::uint8_t>(p[6]);
        hb.systemStatus   = std::to_integer<std::uint8_t>(p[7]);
        hb.mavlinkVersion = std::to_integer<std::uint8_t>(p[8]);
        return Message{hb};
    }
    case kMsgManualControl: {
        ManualControl mc{};
        mc.x       = readI16(p, 0);
        mc.y       = readI16(p, 2);
        mc.z       = readI16(p, 4);
        mc.r       = readI16(p, 6);
        mc.buttons = readU16(p, 8);
        mc.target  = std::to_integer<std::uint8_t>(p[10]);
        return Message{mc};
    }
    case kMsgCommandLong: {
        CommandLong cl{};
        for (std::size_t i = 0; i < cl.param.size(); ++i)
            cl.param[i] = readF32(p, i * 4);
        cl.command         = readU16(p, 28);
        cl.targetSystem    = std::to_integer<std::uint8_t>(p[30]);
        cl.targetComponent = std::to_integer<std::uint8_t>(p[31]);
        cl.confirmation    = std::to_integer<std::uint8_t>(p[32]);
        return Message{cl};
    }
    case kMsgCommandAck: {
        CommandAck ack{};
        ack.command = readU16(p, 0);
        ack.result  = static_cast<Result>(std::to_integer<std::uint8_t>(p[2]));
        return Message{ack};
    }
    default:
        return std::nullopt;
    }
}

std::size_t encode(std::span<std::byte> out, const Message& msg,
                   std::uint8_t sysid, std::uint8_t compid, std::uint8_t seq) noexcept
{
    std::array<std::byte, kMaxPayload> payload{};
    const std::span<std::byte> p{payload};
    std::uint32_t msgid = 0;
    std::uint8_t  len   = 0;

    std::visit(Overloaded{
        [&](const Heartbeat& hb) {
            msgid = kMsgHeartbeat;
            writeU32(p, 0, hb.customMode);
            p[4] = std::byte{hb.type};
            p[5] = std::byte{hb.autopilot};
            p[6] = std::byte{hb.baseMode};
            p[7] = std::byte{hb.systemStatus};
            p[8] = std::byte{hb.mavlinkVersion};
            len  = 9;
        },
        [&](const ManualControl& mc) {
            msgid = kMsgManualControl;
            writeI16(p, 0, mc.x);
            writeI16(p, 2, mc.y);
            writeI16(p, 4, mc.z);
            writeI16(p, 6, mc.r);
            writeU16(p, 8, mc.buttons);
            p[10] = std::byte{mc.target};
            len   = 11;
        },
        [&](const CommandLong& cl) {
            msgid = kMsgCommandLong;
            for (std::size_t i = 0; i < cl.param.size(); ++i)
                writeF32(p, i * 4, cl.param[i]);
            writeU16(p, 28, cl.command);
            p[30] = std::byte{cl.targetSystem};
            p[31] = std::byte{cl.targetComponent};
            p[32] = std::byte{cl.confirmation};
            len   = 33;
        },
        [&](const CommandAck& ack) {
            msgid = kMsgCommandAck;
            writeU16(p, 0, ack.command);
            p[2]  = std::byte{static_cast<std::uint8_t>(ack.result)};
            len   = 3;
        }}, msg);

    const auto info = msgInfo(msgid);
    if (!info)
        return 0;

    // Обрізання хвостових нулів — правило кадру v2; один байт лишається завжди.
    while (len > 1 && payload[len - 1] == std::byte{0})
        --len;

    const std::size_t total = static_cast<std::size_t>(len) + 12U;
    if (out.size() < total)
        return 0;

    std::size_t n = 0;
    out[n++] = kStxV2;
    out[n++] = std::byte{len};
    out[n++] = std::byte{0};  // incompat_flags: без підпису
    out[n++] = std::byte{0};  // compat_flags
    out[n++] = std::byte{seq};
    out[n++] = std::byte{sysid};
    out[n++] = std::byte{compid};
    out[n++] = std::byte{static_cast<std::uint8_t>(msgid)};
    out[n++] = std::byte{static_cast<std::uint8_t>(msgid >> 8)};
    out[n++] = std::byte{static_cast<std::uint8_t>(msgid >> 16)};
    for (std::uint8_t i = 0; i < len; ++i)
        out[n++] = payload[i];

    std::uint16_t crc = 0xFFFFU;
    for (std::size_t i = 1; i < n; ++i)  // CRC рахується з байта довжини
        crcAccumulate(crc, std::to_integer<std::uint8_t>(out[i]));
    crcAccumulate(crc, info->crcExtra);

    out[n++] = std::byte{static_cast<std::uint8_t>(crc & 0xFFU)};
    out[n++] = std::byte{static_cast<std::uint8_t>(crc >> 8)};
    return n;
}

}  // namespace mavlink

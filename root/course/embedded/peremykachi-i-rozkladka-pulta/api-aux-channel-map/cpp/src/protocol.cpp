#include "rc/protocol.hpp"

#include <algorithm>

#include "rc/switches.hpp"

namespace rc {

std::string_view describe(ParseError err) noexcept
{
    switch (err) {
    case ParseError::TooShort:   return "кадр коротший за очікуваний";
    case ParseError::BadAddress: return "чужа адреса призначення";
    case ParseError::BadLength:  return "невірне поле довжини";
    case ParseError::BadType:    return "не той тип кадру";
    case ParseError::BadCrc:     return "CRC8 не збігся";
    case ParseError::BadHeader:  return "невірний стартовий байт";
    case ParseError::BadFooter:  return "неприпустимий стоповий байт";
    }
    return "невідома помилка";
}

namespace crsf {

std::uint8_t crc8(std::span<const std::uint8_t> data) noexcept
{
    std::uint8_t crc = 0;
    for (std::uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            crc = static_cast<std::uint8_t>((crc & 0x80) ? ((crc << 1) ^ kCrcPoly) : (crc << 1));
        }
    }
    return crc;
}

std::expected<RawChannels, ParseError> parseRcChannels(std::span<const std::uint8_t> frame) noexcept
{
    if (frame.size() < kRcFrameSize) {
        return std::unexpected{ParseError::TooShort};
    }
    if (frame[0] != kAddrFlightController) {
        return std::unexpected{ParseError::BadAddress};
    }
    if (frame[1] != kRcLengthField) {
        return std::unexpected{ParseError::BadLength};
    }
    if (frame[2] != kFrameTypeRcChannelsPacked) {
        return std::unexpected{ParseError::BadType};
    }
    // CRC покриває тип і корисне навантаження: байти 2..24
    if (crc8(frame.subspan(2, 1 + kPackedBytes)) != frame[kRcFrameSize - 1]) {
        return std::unexpected{ParseError::BadCrc};
    }

    return unpack11Bit(frame.subspan(3).first<kPackedBytes>());
}

RcFrame buildRcChannels(const RawChannels& raw) noexcept
{
    RcFrame frame{};
    frame[0] = kAddrFlightController;
    frame[1] = kRcLengthField;
    frame[2] = kFrameTypeRcChannelsPacked;

    const PackedPayload payload = pack11Bit(raw);
    std::copy(payload.begin(), payload.end(), frame.begin() + 3);
    frame[kRcFrameSize - 1] = crc8(std::span{frame}.subspan(2, 1 + kPackedBytes));
    return frame;
}

}  // namespace crsf

namespace sbus {

std::expected<Packet, ParseError> parse(std::span<const std::uint8_t> frame) noexcept
{
    if (frame.size() < kFrameSize) {
        return std::unexpected{ParseError::TooShort};
    }
    if (frame[0] != kHeader) {
        return std::unexpected{ParseError::BadHeader};
    }
    if (frame[kFrameSize - 1] != kFooter && frame[kFrameSize - 1] != kFooterV2) {
        return std::unexpected{ParseError::BadFooter};
    }

    Packet packet{};
    packet.channels = unpack11Bit(frame.subspan(1).first<kPackedBytes>());

    const std::uint8_t flags = frame[23];
    packet.ch17      = (flags & kFlagCh17) != 0;
    packet.ch18      = (flags & kFlagCh18) != 0;
    packet.frameLost = (flags & kFlagFrameLost) != 0;
    packet.failsafe  = (flags & kFlagFailsafe) != 0;
    return packet;
}

Frame build(const Packet& packet) noexcept
{
    Frame frame{};
    frame[0] = kHeader;

    const PackedPayload payload = pack11Bit(packet.channels);
    std::copy(payload.begin(), payload.end(), frame.begin() + 1);

    std::uint8_t flags = 0;
    if (packet.ch17)      { flags |= kFlagCh17; }
    if (packet.ch18)      { flags |= kFlagCh18; }
    if (packet.frameLost) { flags |= kFlagFrameLost; }
    if (packet.failsafe)  { flags |= kFlagFailsafe; }

    frame[23] = flags;
    frame[24] = kFooter;
    return frame;
}

}  // namespace sbus

LinkMonitor::LinkMonitor(ChannelMap map, FailsafePolicy policy, std::size_t modeChannel) noexcept
    : map_{map}, policy_{policy}, modeChannel_{modeChannel}
{
    us_.fill(kUsCenter);
}

void LinkMonitor::onFrame(const RawChannels& raw, std::chrono::milliseconds now,
                          bool rxFailsafeBit) noexcept
{
    us_ = toMicros(raw);
    if (rxFailsafeBit) {
        // Біт у самому кадрі — приймач уже визнав втрату лінку
        failsafe_ = true;
        return;
    }
    lastFrame_ = now;
    failsafe_  = false;
}

void LinkMonitor::applyPolicy() noexcept
{
    if (policy_ == FailsafePolicy::HoldLastState) {
        // Нічого не робимо — і саме тому цей режим заборонений
        return;
    }
    us_[channelIndex(map_, Axis::Throttle)] = kFailsafeThrottleUs;
    us_[modeChannel_] = nominalUs(FlightMode::Rtl);
}

bool LinkMonitor::tick(std::chrono::milliseconds now) noexcept
{
    if (!failsafe_ && (now - lastFrame_) > kFailsafeTimeout) {
        failsafe_ = true;
    }
    if (failsafe_) {
        applyPolicy();
    }
    return failsafe_;
}

}  // namespace rc

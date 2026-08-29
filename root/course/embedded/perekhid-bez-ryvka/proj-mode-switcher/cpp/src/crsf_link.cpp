#include "crsf_link.hpp"

#include <algorithm>
#include <cmath>

namespace fc::crsf {
namespace {

// Шкала CRSF: 172 ≈ 988 мкс, 1811 ≈ 2012 мкс.
constexpr float kScale = 0.62477f;
constexpr float kOffset = 881.0f;

}  // namespace

float Channels::microseconds(std::size_t index) const noexcept
{
    if (index >= raw.size()) return kOffset + kScale * 992.0f;
    return kScale * static_cast<float>(raw[index]) + kOffset;
}

float Channels::unit(std::size_t index) const noexcept
{
    const float u = std::clamp((microseconds(index) - 988.0f) / 1024.0f, 0.0f, 1.0f);
    // Крок кванта ≈0.06 %; округлюємо до 0.1 %, щоб останній біт не дрижав.
    return std::round(u * 1000.0f) / 1000.0f;
}

std::uint8_t crc8(std::span<const std::uint8_t> data) noexcept
{
    std::uint8_t crc = 0;
    for (const std::uint8_t byte : data) {          // CRC8/DVB-S2, поліном 0xD5
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit)
            crc = (crc & 0x80u) ? static_cast<std::uint8_t>((crc << 1) ^ 0xD5u)
                                : static_cast<std::uint8_t>(crc << 1);
    }
    return crc;
}

std::expected<Channels, Error> parse(std::span<const std::uint8_t> frame) noexcept
{
    if (frame.size() < kFrameSize) return std::unexpected{Error::ShortFrame};
    if (frame[0] != kAddressFlightController) return std::unexpected{Error::BadAddress};
    if (frame[1] != kPayloadLen) return std::unexpected{Error::BadLength};
    if (frame[2] != kTypeRcChannelsPacked) return std::unexpected{Error::WrongType};
    // CRC рахується від байта типу до останнього байта даних.
    if (crc8(frame.subspan(2, 23)) != frame[25]) return std::unexpected{Error::BadCrc};

    const auto payload = frame.subspan(3, 22);
    Channels out{};
    std::uint32_t acc = 0;
    int bits = 0;
    std::size_t index = 0;
    for (auto& channel : out.raw) {                 // 16 каналів по 11 біт
        while (bits < 11) {
            acc |= static_cast<std::uint32_t>(payload[index++]) << bits;
            bits += 8;
        }
        channel = static_cast<std::uint16_t>(acc & 0x7FFu);
        acc >>= 11;
        bits -= 11;
    }
    return out;
}

std::array<std::uint8_t, kFrameSize> pack(const Channels& channels) noexcept
{
    std::array<std::uint8_t, kFrameSize> frame{};
    frame[0] = kAddressFlightController;
    frame[1] = kPayloadLen;
    frame[2] = kTypeRcChannelsPacked;

    std::uint32_t acc = 0;
    int bits = 0;
    std::size_t index = 3;
    for (const std::uint16_t channel : channels.raw) {
        acc |= static_cast<std::uint32_t>(channel & 0x7FFu) << bits;
        bits += 11;
        while (bits >= 8) {
            frame[index++] = static_cast<std::uint8_t>(acc & 0xFFu);
            acc >>= 8;
            bits -= 8;
        }
    }
    frame[25] = crc8(std::span<const std::uint8_t>{frame}.subspan(2, 23));
    return frame;
}

SwitchPos switch_position(float microseconds, SwitchPos previous) noexcept
{
    constexpr float lo = 1300.0f;
    constexpr float hi = 1700.0f;
    constexpr float hyst = 40.0f;

    switch (previous) {
    case SwitchPos::Low:
        if (microseconds > hi + hyst) return SwitchPos::High;
        if (microseconds > lo + hyst) return SwitchPos::Mid;
        return SwitchPos::Low;
    case SwitchPos::High:
        if (microseconds < lo - hyst) return SwitchPos::Low;
        if (microseconds < hi - hyst) return SwitchPos::Mid;
        return SwitchPos::High;
    case SwitchPos::Mid:
        break;
    }
    if (microseconds > hi + hyst) return SwitchPos::High;
    if (microseconds < lo - hyst) return SwitchPos::Low;
    return SwitchPos::Mid;
}

std::expected<Channels, Error> Link::feed(std::span<const std::uint8_t> frame,
                                          Millis now) noexcept
{
    auto decoded = parse(frame);
    if (!decoded) {
        if (decoded.error() == Error::BadCrc) ++crc_errors_;
        else ++format_errors_;
        return decoded;
    }
    channels_ = *decoded;
    last_ok_ = now;
    have_data_ = true;
    failsafe_ = false;
    ++frames_ok_;
    return decoded;
}

bool Link::tick(Millis now) noexcept
{
    failsafe_ = !have_data_ || (now - last_ok_ > kFailsafeTimeout);
    return failsafe_;
}

}  // namespace fc::crsf

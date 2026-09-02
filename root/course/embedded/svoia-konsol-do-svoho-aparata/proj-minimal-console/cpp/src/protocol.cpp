#include "protocol.hpp"

namespace console {
namespace {

// Пише значення бітовим потоком, молодшим бітом уперед.
class BitWriter {
public:
    explicit BitWriter(std::span<std::byte> out, std::size_t startBit) noexcept
        : out_{out}, bit_{startBit}
    {
    }

    void put(std::uint32_t value, std::uint8_t bits) noexcept
    {
        for (std::uint8_t i = 0; i < bits; ++i) {
            if (value & (1u << i)) {
                out_[bit_ >> 3] |= static_cast<std::byte>(1u << (bit_ & 7u));
            }
            ++bit_;
        }
    }

private:
    std::span<std::byte> out_;
    std::size_t bit_;
};

constexpr std::uint16_t readU16(std::span<const std::byte> raw, std::size_t offset) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(raw[offset]) |
                                      (std::to_integer<std::uint16_t>(raw[offset + 1]) << 8));
}

}   // namespace

Frame UplinkFrame::serialize() const noexcept
{
    Frame frame{};
    frame[0] = kUplinkSync;
    frame[1] = static_cast<std::byte>(sequence);

    // Чотири одинадцятибітні осі — це 44 біти; вони лягають у байти 2..7,
    // чотири останні біти лишаються нулями під майбутній п'ятий канал.
    BitWriter writer{frame, 16};
    for (std::uint16_t axis : axes) {
        writer.put(axis & 0x07FFu, 11);
    }

    frame[8] = static_cast<std::byte>(switches & 0xFF);
    frame[9] = static_cast<std::byte>(switches >> 8);
    frame[10] = static_cast<std::byte>(flags);
    frame[11] = static_cast<std::byte>(aux);

    const std::uint16_t crc = crc16(std::span<const std::byte>{frame}.first(kFrameLength - 2));
    frame[12] = static_cast<std::byte>(crc >> 8);
    frame[13] = static_cast<std::byte>(crc);
    return frame;
}

std::expected<Telemetry, ProtoError> Telemetry::parse(std::span<const std::byte> raw) noexcept
{
    if (raw.size() != kFrameLength) {
        return std::unexpected{ProtoError::WrongLength};
    }
    if (raw[0] != kDownlinkSync) {
        return std::unexpected{ProtoError::WrongSync};
    }
    // Контрольна сума в кадрі лежить старшим байтом уперед, решта полів —
    // молодшим: так само, як їх кладе борт.
    const auto carried = static_cast<std::uint16_t>(
        (std::to_integer<std::uint16_t>(raw[12]) << 8) | std::to_integer<std::uint16_t>(raw[13]));
    if (crc16(raw.first(kFrameLength - 2)) != carried) {
        return std::unexpected{ProtoError::CrcMismatch};
    }

    Telemetry telemetry{};
    telemetry.sequence = std::to_integer<std::uint8_t>(raw[1]);
    telemetry.vbatMv = readU16(raw, 2);
    telemetry.currentDeciAmp = readU16(raw, 4);
    // У кадрі їде модуль рівня сигналу — знак додаємо тут.
    telemetry.rssiDbm = static_cast<std::int8_t>(-std::to_integer<int>(raw[6]));
    telemetry.linkPercent = std::min<std::uint8_t>(std::to_integer<std::uint8_t>(raw[7]), 100);
    telemetry.mosTempC = std::to_integer<std::uint8_t>(raw[8]);
    telemetry.flightMode = std::to_integer<std::uint8_t>(raw[9]);
    telemetry.satellites = std::to_integer<std::uint8_t>(raw[10]);
    telemetry.status = std::to_integer<std::uint8_t>(raw[11]);
    return telemetry;
}

}   // namespace console

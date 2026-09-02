#include "msp.hpp"

#include <algorithm>

namespace msp {
namespace {

// Читач із межами: після першого виходу за буфер усе решта віддає нулі,
// а ok() лишається false — перевіряти досить один раз у кінці.
class Cursor {
public:
    explicit Cursor(std::span<const std::byte> data) noexcept : data_{data} {}

    [[nodiscard]] bool ok() const noexcept { return ok_; }

    std::uint8_t u8() noexcept
    {
        if (!ok_ || pos_ >= data_.size()) {
            ok_ = false;
            return 0;
        }
        return std::to_integer<std::uint8_t>(data_[pos_++]);
    }

    std::uint16_t u16() noexcept
    {
        const std::uint16_t lo = u8();
        const std::uint16_t hi = u8();
        return static_cast<std::uint16_t>(lo | (hi << 8));
    }

    std::uint32_t u32() noexcept
    {
        const std::uint32_t b0 = u8();
        const std::uint32_t b1 = u8();
        const std::uint32_t b2 = u8();
        const std::uint32_t b3 = u8();
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
    }

    std::vector<std::byte> bytes(std::size_t count)
    {
        std::vector<std::byte> out;
        out.reserve(count);
        for (std::size_t i = 0; i < count; ++i) {
            out.push_back(std::byte{u8()});
        }
        return out;
    }

private:
    std::span<const std::byte> data_;
    std::size_t pos_{0};
    bool ok_{true};
};

[[nodiscard]] std::uint8_t checksum(std::uint8_t size, std::uint8_t code,
                                    std::span<const std::byte> payload) noexcept
{
    std::uint8_t crc = static_cast<std::uint8_t>(size ^ code);
    for (const std::byte b : payload) {
        crc ^= std::to_integer<std::uint8_t>(b);
    }
    return crc;
}

}  // namespace

std::string_view describe(Error error) noexcept
{
    switch (error) {
    case Error::TooShort:         return "кадр коротший за шапку";
    case Error::BadMagic:         return "немає префікса $M";
    case Error::NotAReply:        return "це не відповідь плати ('<' або '!')";
    case Error::LengthMismatch:   return "довжина буфера не збігається з полем size";
    case Error::Checksum:         return "контрольна сума не збіглася";
    case Error::UnexpectedCode:   return "код повідомлення не MSP_STATUS";
    case Error::TruncatedPayload: return "payload обірвано — прошивка віддала менше полів";
    }
    return "невідома помилка";
}

std::expected<Status, Error> parseStatus(std::span<const std::byte> frame)
{
    if (frame.size() < 6) {
        return std::unexpected{Error::TooShort};
    }
    if (frame[0] != std::byte{'$'} || frame[1] != std::byte{'M'}) {
        return std::unexpected{Error::BadMagic};
    }
    if (frame[2] != std::byte{'>'}) {
        return std::unexpected{Error::NotAReply};
    }

    const auto size = std::to_integer<std::uint8_t>(frame[3]);
    const auto code = std::to_integer<std::uint8_t>(frame[4]);
    if (frame.size() != static_cast<std::size_t>(size) + 6) {
        return std::unexpected{Error::LengthMismatch};
    }

    const std::span<const std::byte> payload = frame.subspan(5, size);
    if (checksum(size, code, payload) != std::to_integer<std::uint8_t>(frame[5 + size])) {
        return std::unexpected{Error::Checksum};
    }
    if (code != kStatus) {
        return std::unexpected{Error::UnexpectedCode};
    }

    Cursor cursor{payload};
    Status status;
    status.cycleTimeUs = cursor.u16();
    status.i2cErrors = cursor.u16();
    status.sensors = cursor.u16();
    status.flightModeFlags = cursor.u32();
    status.pidProfile = cursor.u8();
    status.cpuLoadPercent = cursor.u16();
    status.gyroCycleTimeUs = cursor.u16();

    // Довжина блоку додаткових BOX-прапорців змінна — без неї до маски
    // блокувань не дійти, і саме тут ламаються саморобні парсери.
    const auto extraCount = static_cast<std::size_t>(cursor.u8() & 0x0Fu);
    status.extraModeFlags = cursor.bytes(extraCount);

    status.armingFlagCount = cursor.u8();
    status.armingDisable = bf::Mask{cursor.u32()};
    status.configState = cursor.u8();

    if (!cursor.ok()) {
        return std::unexpected{Error::TruncatedPayload};
    }
    return status;
}

std::vector<std::byte> buildRequest(std::uint8_t code)
{
    return {std::byte{'$'}, std::byte{'M'}, std::byte{'<'},
            std::byte{0}, std::byte{code}, std::byte{code}};
}

std::vector<std::byte> encodeStatus(const Status& status)
{
    std::vector<std::byte> payload;
    const auto put8 = [&payload](std::uint32_t value) {
        payload.push_back(std::byte{static_cast<std::uint8_t>(value & 0xFFu)});
    };
    const auto put16 = [&put8](std::uint32_t value) {
        put8(value);
        put8(value >> 8);
    };
    const auto put32 = [&put16](std::uint32_t value) {
        put16(value);
        put16(value >> 16);
    };

    put16(status.cycleTimeUs);
    put16(status.i2cErrors);
    put16(status.sensors);
    put32(status.flightModeFlags);
    put8(status.pidProfile);
    put16(status.cpuLoadPercent);
    put16(status.gyroCycleTimeUs);

    const std::size_t extra = std::min(status.extraModeFlags.size(), kMaxExtraModeFlags);
    put8(static_cast<std::uint32_t>(extra));
    payload.insert(payload.end(), status.extraModeFlags.begin(),
                   status.extraModeFlags.begin() + static_cast<std::ptrdiff_t>(extra));

    put8(status.armingFlagCount);
    put32(status.armingDisable.raw());
    put8(status.configState);

    const auto size = static_cast<std::uint8_t>(payload.size());
    std::vector<std::byte> frame{std::byte{'$'}, std::byte{'M'}, std::byte{'>'},
                                std::byte{size}, std::byte{kStatus}};
    frame.insert(frame.end(), payload.begin(), payload.end());
    frame.push_back(std::byte{checksum(size, kStatus, payload)});
    return frame;
}

}  // namespace msp

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <cmath>

namespace telemetry {

inline constexpr uint8_t FrameMagic   = 0x50;
inline constexpr uint8_t FrameVersion = 0x01;
inline constexpr size_t  FrameSize    = 13;

enum class UnpackError {
    BufferTooSmall,
    InvalidMagic,
    UnsupportedVersion,
    CrcMismatch
};

struct TelemetryData {
    uint32_t timestamp{0};
    int16_t  temp_centi_deg{0};
    uint16_t batt_millivolts{0};
    uint8_t  hum_half_pct{0};
    uint8_t  flags{0};

    [[nodiscard]] double temperature_celsius() const noexcept {
        return static_cast<double>(temp_centi_deg) / 100.0;
    }

    [[nodiscard]] double battery_volts() const noexcept {
        return static_cast<double>(batt_millivolts) / 1000.0;
    }

    [[nodiscard]] double humidity_pct() const noexcept {
        return static_cast<double>(hum_half_pct) * 0.5;
    }

    static TelemetryData from_physical(uint32_t ts, double temp, double batt_v, double hum, uint8_t fl) noexcept {
        TelemetryData d{};
        d.timestamp = ts;
        d.temp_centi_deg = static_cast<int16_t>(std::lround(temp * 100.0));
        d.batt_millivolts = static_cast<uint16_t>(std::lround(batt_v * 1000.0));
        d.hum_half_pct = static_cast<uint8_t>(std::clamp(std::lround(hum * 2.0), 0L, 200L));
        d.flags = fl;
        return d;
    }
};

class FramePacker {
public:
    static constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    static bool pack(const TelemetryData& src, std::span<uint8_t> dst) noexcept {
        if (dst.size() < FrameSize) {
            return false;
        }

        dst[0] = (FrameMagic & 0xF0) | (FrameVersion & 0x0F);

        dst[1] = static_cast<uint8_t>((src.timestamp >> 24) & 0xFF);
        dst[2] = static_cast<uint8_t>((src.timestamp >> 16) & 0xFF);
        dst[3] = static_cast<uint8_t>((src.timestamp >> 8) & 0xFF);
        dst[4] = static_cast<uint8_t>(src.timestamp & 0xFF);

        const auto raw_temp = static_cast<uint16_t>(src.temp_centi_deg);
        dst[5] = static_cast<uint8_t>((raw_temp >> 8) & 0xFF);
        dst[6] = static_cast<uint8_t>(raw_temp & 0xFF);

        dst[7] = static_cast<uint8_t>((src.batt_millivolts >> 8) & 0xFF);
        dst[8] = static_cast<uint8_t>(src.batt_millivolts & 0xFF);

        dst[9]  = src.hum_half_pct;
        dst[10] = src.flags;

        const uint16_t crc = calculate_crc16(dst.subspan(0, 11));
        dst[11] = static_cast<uint8_t>((crc >> 8) & 0xFF);
        dst[12] = static_cast<uint8_t>(crc & 0xFF);

        return true;
    }

    [[nodiscard]] static std::expected<TelemetryData, UnpackError> unpack(
        std::span<const uint8_t> src) noexcept {
        if (src.size() < FrameSize) {
            return std::unexpected(UnpackError::BufferTooSmall);
        }

        const uint8_t header = src[0];
        if ((header & 0xF0) != (FrameMagic & 0xF0)) {
            return std::unexpected(UnpackError::InvalidMagic);
        }
        if ((header & 0x0F) != FrameVersion) {
            return std::unexpected(UnpackError::UnsupportedVersion);
        }

        const uint16_t expected_crc = (static_cast<uint16_t>(src[11]) << 8) | src[12];
        const uint16_t actual_crc = calculate_crc16(src.subspan(0, 11));
        if (expected_crc != actual_crc) {
            return std::unexpected(UnpackError::CrcMismatch);
        }

        TelemetryData result{};
        result.timestamp = (static_cast<uint32_t>(src[1]) << 24) |
                           (static_cast<uint32_t>(src[2]) << 16) |
                           (static_cast<uint32_t>(src[3]) << 8)  |
                           static_cast<uint32_t>(src[4]);

        result.temp_centi_deg  = static_cast<int16_t>((static_cast<uint16_t>(src[5]) << 8) | src[6]);
        result.batt_millivolts = (static_cast<uint16_t>(src[7]) << 8) | src[8];
        result.hum_half_pct    = src[9];
        result.flags           = src[10];

        return result;
    }
};

} // namespace telemetry

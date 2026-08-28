#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <array>

enum class ProtoStatus : uint8_t {
    Ok = 0x00,
    InvalidSof = 0x01,
    InvalidEof = 0x02,
    InvalidCrc = 0x03,
    InvalidLen = 0x04,
    UnknownMsg = 0x05
};

enum class MsgType : uint8_t {
    Ping = 0x01,
    SetConfig = 0x02,
    TelemetryReport = 0x20,
    Response = 0x80
};

struct TelemetryReport {
    int16_t temp_raw;
    uint16_t pressure_raw;
    uint16_t voltage_mv;
    uint8_t flags;
    uint8_t reserved;

    [[nodiscard]] constexpr double temperature_c() const noexcept {
        return temp_raw * 0.01;
    }
    [[nodiscard]] constexpr double pressure_hpa() const noexcept {
        return pressure_raw * 0.1;
    }
};

class FrameParser {
public:
    static constexpr uint8_t SofMarker = 0xAA;
    static constexpr uint8_t EofMarker = 0x55;
    static constexpr size_t HeaderLen = 6;
    static constexpr size_t FooterLen = 3;
    static constexpr size_t MinFrameLen = HeaderLen + FooterLen;

    [[nodiscard]] static constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
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

    [[nodiscard]] static std::expected<TelemetryReport, ProtoStatus> parse_telemetry(
        std::span<const uint8_t> frame) noexcept 
    {
        if (frame.size() < MinFrameLen + sizeof(TelemetryReport)) {
            return std::unexpected(ProtoStatus::InvalidLen);
        }
        if (frame.front() != SofMarker) {
            return std::unexpected(ProtoStatus::InvalidSof);
        }
        if (frame.back() != EofMarker) {
            return std::unexpected(ProtoStatus::InvalidEof);
        }
        if (static_cast<MsgType>(frame[2]) != MsgType::TelemetryReport) {
            return std::unexpected(ProtoStatus::UnknownMsg);
        }

        const uint16_t payload_len = static_cast<uint16_t>(frame[4]) | 
                                    (static_cast<uint16_t>(frame[5]) << 8);
        if (payload_len != 8 || frame.size() != HeaderLen + payload_len + FooterLen) {
            return std::unexpected(ProtoStatus::InvalidLen);
        }

        const uint16_t expected_crc = static_cast<uint16_t>(frame[frame.size() - 3]) |
                                     (static_cast<uint16_t>(frame[frame.size() - 2]) << 8);
        const uint16_t actual_crc = calculate_crc16(frame.subspan(1, HeaderLen - 1 + payload_len));
        if (actual_crc != expected_crc) {
            return std::unexpected(ProtoStatus::InvalidCrc);
        }

        const auto payload = frame.subspan(HeaderLen, payload_len);
        TelemetryReport report{
            .temp_raw = static_cast<int16_t>(static_cast<uint16_t>(payload[0]) | (static_cast<uint16_t>(payload[1]) << 8)),
            .pressure_raw = static_cast<uint16_t>(payload[2]) | static_cast<uint16_t>(payload[3] << 8),
            .voltage_mv = static_cast<uint16_t>(payload[4]) | static_cast<uint16_t>(payload[5] << 8),
            .flags = payload[6],
            .reserved = payload[7]
        };

        return report;
    }
};

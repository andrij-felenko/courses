// minimal_remote_firmware.hpp — Ідіоматична реалізація прошивки на C++20
#pragma once
#include <cstdint>
#include <array>
#include <span>
#include <algorithm>
#include <cstring>

namespace remote {

inline constexpr uint8_t FrameSyncByte = 0x5A;
inline constexpr std::size_t AxisCount = 4;

struct CalibrationData {
    uint16_t min_raw{320};
    uint16_t center_raw{2048};
    uint16_t max_raw{3780};
    uint16_t deadband{25};
};

struct [[gnu::packed]] UplinkPacket {
    uint8_t  sync{FrameSyncByte};
    uint8_t  sequence{0};
    std::array<uint8_t, 6> packed_channels{};
    uint8_t  switches{0};
    uint8_t  flags{0};
    uint16_t crc{0};
};

struct [[gnu::packed]] DownlinkTelemetry {
    uint8_t  sync{0};
    uint8_t  sequence{0};
    uint16_t vbat_mv{0};
    uint8_t  current_a_x10{0};
    uint8_t  rssi_dbm{0};
    uint8_t  link_quality{0};
    uint8_t  flight_mode{0};
};

class RemoteController {
public:
    constexpr RemoteController() = default;

    void setCalibration(std::size_t axis, const CalibrationData& calib) noexcept {
        if (axis < AxisCount) {
            calibration_[axis] = calib;
        }
    }

    [[nodiscard]] uint16_t processAxis(std::size_t ch, uint16_t raw_adc) noexcept {
        if (ch >= AxisCount) return 1024;

        // Експоненційний IIR фільтр (вага 0.5)
        filtered_adc_[ch] = static_cast<uint16_t>((raw_adc * 5 + filtered_adc_[ch] * 5) / 10);
        const auto val = std::clamp(filtered_adc_[ch], calibration_[ch].min_raw, calibration_[ch].max_raw);
        const auto& c = calibration_[ch];

        if (ch == 2) { // Throttle
            const auto span = c.max_raw - c.min_raw;
            return span ? static_cast<uint16_t>((static_cast<uint32_t>(val - c.min_raw) * 2047) / span) : 0;
        }

        const int32_t diff = static_cast<int32_t>(val) - static_cast<int32_t>(c.center_raw);
        if (std::abs(diff) < c.deadband) {
            return 1024;
        }

        if (diff > 0) {
            const uint32_t span = c.max_raw - c.center_raw;
            const uint32_t res = 1024 + ((static_cast<uint32_t>(diff) * 1023) / span);
            return static_cast<uint16_t>(std::min<uint32_t>(res, 2047));
        } else {
            const uint32_t span = c.center_raw - c.min_raw;
            const int32_t res = 1024 - ((static_cast<uint32_t>(-diff) * 1024) / span);
            return static_cast<uint16_t>(std::max<int32_t>(res, 0));
        }
    }

    [[nodiscard]] UplinkPacket packControlFrame(std::span<const uint16_t, AxisCount> raw_adc, 
                                                uint8_t switches, uint8_t flags = 0) noexcept {
        std::array<uint16_t, AxisCount> norm{};
        for (std::size_t i = 0; i < AxisCount; ++i) {
            norm[i] = processAxis(i, raw_adc[i]);
        }

        UplinkPacket packet{};
        packet.sync = FrameSyncByte;
        packet.sequence = sequence_counter_++;
        packet.switches = switches;
        packet.flags = flags;

        // Бітове пакування 4x 11-бітних осей у 6 байтів
        packet.packed_channels[0] = static_cast<uint8_t>(norm[0] & 0xFF);
        packet.packed_channels[1] = static_cast<uint8_t>(((norm[0] >> 8) & 0x07) | ((norm[1] & 0x1F) << 3));
        packet.packed_channels[2] = static_cast<uint8_t>(((norm[1] >> 5) & 0x3F) | ((norm[2] & 0x03) << 6));
        packet.packed_channels[3] = static_cast<uint8_t>((norm[2] >> 2) & 0xFF);
        packet.packed_channels[4] = static_cast<uint8_t>(((norm[2] >> 10) & 0x01) | ((norm[3] & 0x7F) << 1));
        packet.packed_channels[5] = static_cast<uint8_t>((norm[3] >> 7) & 0x0F);

        packet.crc = calculateCrc16(std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&packet), sizeof(UplinkPacket) - sizeof(uint16_t)
        });

        return packet;
    }

private:
    static uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t b : data) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (uint8_t i = 0; i < 8; ++i) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }
        return crc;
    }

    std::array<CalibrationData, AxisCount> calibration_{};
    std::array<uint16_t, AxisCount> filtered_adc_{2048, 2048, 0, 2048};
    uint8_t sequence_counter_{0};
};

} // namespace remote

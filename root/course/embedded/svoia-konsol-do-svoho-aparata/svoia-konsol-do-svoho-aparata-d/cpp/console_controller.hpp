// console_controller.hpp — Модуль керування на ідіоматичному C++20
#pragma once
#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

namespace console {

inline constexpr std::size_t ChannelCount = 4;
inline constexpr uint16_t ChannelMax11Bit = 2047;
inline constexpr uint16_t DeadbandThreshold = 30;

struct GimbalCalibration {
    uint16_t min{350};
    uint16_t center{2048};
    uint16_t max{3750};
    uint16_t deadband{DeadbandThreshold};
};

struct [[gnu::packed]] RadioControlFrame {
    uint8_t  sync_byte{0x5A};
    uint8_t  sequence_id{0};
    std::array<uint8_t, 6> packed_axes{};
    uint8_t  switches_mask{0};
    uint8_t  command_flags{0};
    uint16_t crc16{0};
};

class ControllerEngine {
public:
    constexpr ControllerEngine() = default;

    void setCalibration(std::size_t ch, const GimbalCalibration& calib) noexcept {
        if (ch < ChannelCount) {
            calibration_[ch] = calib;
        }
    }

    [[nodiscard]] uint16_t processAxis(std::size_t ch, uint16_t raw_adc) noexcept {
        if (ch >= ChannelCount) return ChannelMax11Bit / 2;

        // Експоненційний IIR фільтр (вага 0.5)
        filtered_adc_[ch] = static_cast<uint16_t>((raw_adc + filtered_adc_[ch]) >> 1);
        const auto val = std::clamp(filtered_adc_[ch], calibration_[ch].min, calibration_[ch].max);
        const auto& c = calibration_[ch];

        // Вісь газу (Throttle без нейтрального центру)
        if (ch == 2) {
            const auto span = c.max - c.min;
            return span ? static_cast<uint16_t>((static_cast<uint32_t>(val - c.min) * ChannelMax11Bit) / span) : 0;
        }

        const int32_t delta = static_cast<int32_t>(val) - static_cast<int32_t>(c.center);
        if (std::abs(delta) < c.deadband) {
            return ChannelMax11Bit / 2; // Ідеальний нуль у центрі
        }

        if (delta > 0) {
            const uint32_t span = c.max - c.center;
            const uint32_t out = (ChannelMax11Bit / 2) + 
                                 ((static_cast<uint32_t>(delta) * (ChannelMax11Bit / 2)) / span);
            return static_cast<uint16_t>(std::min<uint32_t>(out, ChannelMax11Bit));
        } else {
            const uint32_t span = c.center - c.min;
            const int32_t out = (ChannelMax11Bit / 2) - 
                                ((static_cast<uint32_t>(-delta) * (ChannelMax11Bit / 2)) / span);
            return static_cast<uint16_t>(std::max<int32_t>(out, 0));
        }
    }

    [[nodiscard]] RadioControlFrame buildPacket(std::span<const uint16_t, ChannelCount> raw_adc, 
                                                uint8_t switches, uint8_t flags = 0) noexcept {
        std::array<uint16_t, ChannelCount> norm{};
        for (std::size_t i = 0; i < ChannelCount; ++i) {
            norm[i] = processAxis(i, raw_adc[i]);
        }

        RadioControlFrame frame{};
        frame.sync_byte = 0x5A;
        frame.sequence_id = sequence_id_++;
        frame.switches_mask = switches;
        frame.command_flags = flags;

        // Бітове пакування 4x 11-бітних осей у 6 байтів
        frame.packed_axes[0] = static_cast<uint8_t>(norm[0] & 0xFF);
        frame.packed_axes[1] = static_cast<uint8_t>(((norm[0] >> 8) & 0x07) | ((norm[1] & 0x1F) << 3));
        frame.packed_axes[2] = static_cast<uint8_t>(((norm[1] >> 5) & 0x3F) | ((norm[2] & 0x03) << 6));
        frame.packed_axes[3] = static_cast<uint8_t>((norm[2] >> 2) & 0xFF);
        frame.packed_axes[4] = static_cast<uint8_t>(((norm[2] >> 10) & 0x01) | ((norm[3] & 0x7F) << 1));
        frame.packed_axes[5] = static_cast<uint8_t>((norm[3] >> 7) & 0x0F);

        frame.crc16 = calculateCrc16(std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&frame), sizeof(RadioControlFrame) - sizeof(uint16_t)
        });

        return frame;
    }

private:
    static uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }
        return crc;
    }

    std::array<GimbalCalibration, ChannelCount> calibration_{};
    std::array<uint16_t, ChannelCount> filtered_adc_{2048, 2048, 0, 2048};
    uint8_t sequence_id_{0};
};

} // namespace console

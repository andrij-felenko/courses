#ifndef SENSOR_STATE_RECOVERY_HPP
#define SENSOR_STATE_RECOVERY_HPP

#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

template <size_t MaxRegs = 16, size_t MaxCalib = 32>
class SensorShadowCache {
public:
    struct RegisterEntry {
        uint8_t address{0};
        uint8_t value{0};
    };

    constexpr SensorShadowCache() noexcept = default;

    void set_register(uint8_t address, uint8_t value) noexcept {
        for (size_t i = 0; i < reg_count_; ++i) {
            if (registers_[i].address == address) {
                registers_[i].value = value;
                return;
            }
        }
        if (reg_count_ < MaxRegs) {
            registers_[reg_count_++] = {address, value};
        }
    }

    [[nodiscard]] std::span<const RegisterEntry> registers() const noexcept {
        return {registers_.data(), reg_count_};
    }

    void store_calibration(std::span<const uint8_t> calib) noexcept {
        const size_t len = std::min(calib.size(), MaxCalib);
        std::copy_n(calib.data(), len, calib_data_.begin());
        calib_len_ = len;
        calib_crc_ = compute_crc16(calib.subspan(0, len));
        calib_valid_ = true;
    }

    [[nodiscard]] bool verify_calibration(std::span<const uint8_t> calib) const noexcept {
        if (!calib_valid_ || calib.size() != calib_len_) return false;
        return compute_crc16(calib) == calib_crc_;
    }

private:
    std::array<RegisterEntry, MaxRegs> registers_{};
    size_t reg_count_{0};
    std::array<uint8_t, MaxCalib> calib_data_{};
    size_t calib_len_{0};
    uint16_t calib_crc_{0};
    bool calib_valid_{false};

    static constexpr uint16_t compute_crc16(std::span<const uint8_t> data) noexcept {
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
};

#endif // SENSOR_STATE_RECOVERY_HPP

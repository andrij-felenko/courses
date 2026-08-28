/**
 * @file CppImuDriver.hpp
 * @brief Шаблонний C++20 драйвер сенсора з концептуальним зв'язуванням.
 */

#pragma once

#include "BusConcepts.hpp"
#include <array>

namespace embedded::sensor {

struct Acceleration {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

template <typename BusType>
class ImuSensor {
public:
    static constexpr uint8_t REG_CHIP_ID      = 0x00;
    static constexpr uint8_t REG_PWR_MGMT_1   = 0x06;
    static constexpr uint8_t REG_ACCEL_CONFIG = 0x14;
    static constexpr uint8_t REG_ACCEL_XOUT_H = 0x1F;

    static constexpr uint8_t EXPECTED_ID      = 0x42;

    explicit ImuSensor(BusType& bus) : bus_(bus) {}

    [[nodiscard]] std::expected<void, bus::BusError> init() {
        // 1. Зчитування Chip ID
        auto id = bus_.read_u8(REG_CHIP_ID);
        if (!id) return std::unexpected(id.error());
        if (*id != EXPECTED_ID) return std::unexpected(bus::BusError::IoError);

        // 2. Пробудження сенсора
        auto pwr_res = bus_.write_u8(REG_PWR_MGMT_1, 0x01);
        if (!pwr_res) return pwr_res;

        // 3. Конфігурація діапазону ±4g
        auto cfg_res = bus_.write_u8(REG_ACCEL_CONFIG, 0x08);
        if (!cfg_res) return cfg_res;

        accel_scale_ = (4.0f * 9.80665f) / 32768.0f;
        is_ready_    = true;
        return {};
    }

    [[nodiscard]] std::expected<Acceleration, bus::BusError> read_accel() {
        if (!is_ready_) return std::unexpected(bus::BusError::InvalidParam);

        std::array<uint8_t, 6> raw{};
        auto res = bus_.read_reg(REG_ACCEL_XOUT_H, std::span<uint8_t>(raw));
        if (!res) return std::unexpected(res.error());

        auto unpack_be = [](uint8_t msb, uint8_t lsb) noexcept -> int16_t {
            return static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
        };

        Acceleration acc{};
        acc.x = static_cast<float>(unpack_be(raw[0], raw[1])) * accel_scale_;
        acc.y = static_cast<float>(unpack_be(raw[2], raw[3])) * accel_scale_;
        acc.z = static_cast<float>(unpack_be(raw[4], raw[5])) * accel_scale_;

        return acc;
    }

private:
    BusType& bus_;
    float    accel_scale_{0.0f};
    bool     is_ready_{false};
};

} // namespace embedded::sensor

/**
 * @file CppImuDriver.hpp
 * @brief Сучасний C++20 драйвер IMU-сенсора з підтримкою Концептів.
 */

#pragma once

#include "BusConcepts.hpp"
#include <numbers>

namespace embedded::sensor {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct ImuSample {
    Vector3f accel_mps2;
    Vector3f gyro_rads;
    float    temp_celsius{0.0f};
};

/**
 * @brief Шаблонний C++20 драйвер 6-осьового сенсора.
 * @tparam BusClass Тип шини, що задовольняє концепт bus::BusTransport або IBusAdapter.
 */
template <typename BusClass>
class ImuDriver {
public:
    static constexpr uint8_t REG_CHIP_ID   = 0x00;
    static constexpr uint8_t REG_PWR_CTRL  = 0x7D;
    static constexpr uint8_t REG_ACC_CONF  = 0x40;
    static constexpr uint8_t REG_GYR_CONF  = 0x42;
    static constexpr uint8_t REG_ACC_DATA  = 0x12;
    static constexpr uint8_t REG_TEMP_DATA = 0x22;

    static constexpr uint8_t EXPECTED_ID   = 0x24;

    explicit ImuDriver(BusClass& bus) : bus_(bus) {}

    [[nodiscard]] std::expected<void, bus::BusError> init() {
        // 1. Перевірка Chip ID
        uint8_t chip_id = 0;
        auto res = bus_.read_reg(REG_CHIP_ID, std::span<uint8_t>(&chip_id, 1));
        if (!res) return std::unexpected(res.error());

        if (chip_id != EXPECTED_ID) {
            return std::unexpected(bus::BusError::IoError);
        }

        // 2. Увімкнення живлення акселерометра та гіроскопа
        uint8_t pwr_on = 0x0E;
        res = bus_.write_reg(REG_PWR_CTRL, std::span<const uint8_t>(&pwr_on, 1));
        if (!res) return std::unexpected(res.error());

        // 3. Конфігурація діапазонів
        uint8_t acc_cfg = 0xA8; // ±4g
        res = bus_.write_reg(REG_ACC_CONF, std::span<const uint8_t>(&acc_cfg, 1));
        if (!res) return std::unexpected(res.error());

        uint8_t gyr_cfg = 0xA9; // ±2000 dps
        res = bus_.write_reg(REG_GYR_CONF, std::span<const uint8_t>(&gyr_cfg, 1));
        if (!res) return std::unexpected(res.error());

        constexpr float gravity = 9.80665f;
        accel_scale_ = (4.0f * gravity) / 32768.0f;
        gyro_scale_  = (2000.0f * (std::numbers::pi_v<float> / 180.0f)) / 32768.0f;
        initialized_ = true;

        return {};
    }

    [[nodiscard]] std::expected<ImuSample, bus::BusError> read_sample() {
        if (!initialized_) return std::unexpected(bus::BusError::InvalidArg);

        std::array<uint8_t, 12> raw{};
        auto res = bus_.read_reg(REG_ACC_DATA, std::span<uint8_t>(raw));
        if (!res) return std::unexpected(res.error());

        auto unpack_s16 = [](uint8_t lsb, uint8_t msb) noexcept -> int16_t {
            return static_cast<int16_t>(static_cast<uint16_t>(lsb) | (static_cast<uint16_t>(msb) << 8));
        };

        ImuSample sample{};
        sample.accel_mps2.x = static_cast<float>(unpack_s16(raw[0], raw[1])) * accel_scale_;
        sample.accel_mps2.y = static_cast<float>(unpack_s16(raw[2], raw[3])) * accel_scale_;
        sample.accel_mps2.z = static_cast<float>(unpack_s16(raw[4], raw[5])) * accel_scale_;

        sample.gyro_rads.x  = static_cast<float>(unpack_s16(raw[6], raw[7])) * gyro_scale_;
        sample.gyro_rads.y  = static_cast<float>(unpack_s16(raw[8], raw[9])) * gyro_scale_;
        sample.gyro_rads.z  = static_cast<float>(unpack_s16(raw[10], raw[11])) * gyro_scale_;

        std::array<uint8_t, 2> temp_raw{};
        if (bus_.read_reg(REG_TEMP_DATA, std::span<uint8_t>(temp_raw))) {
            int16_t raw_temp = unpack_s16(temp_raw[0], temp_raw[1]);
            sample.temp_celsius = 23.0f + (static_cast<float>(raw_temp) / 512.0f);
        }

        return sample;
    }

private:
    BusClass& bus_;
    float     accel_scale_{0.0f};
    float     gyro_scale_{0.0f};
    bool      initialized_{false};
};

} // namespace embedded::sensor

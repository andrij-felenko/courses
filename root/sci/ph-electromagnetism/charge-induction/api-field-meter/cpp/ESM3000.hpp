// ESM3000.hpp - Об'єктно-орієнтований C++20 API драйвер ESM-3000
#pragma once

#include <cstdint>
#include <expected>
#include <string_view>
#include <cmath>

namespace esm {

enum class FieldRange : std::uint8_t {
    Range1kV   = 0x00,
    Range5kV   = 0x01,
    Range20kV  = 0x02,
    Range100kV = 0x03
};

enum class DriverError {
    CommunicationFailed,
    InvalidDeviceID,
    DeviceSaturated,
    SelfTestFailed
};

struct FieldData {
    float field_kv_per_m{0.0f};
    float induced_charge_nc{0.0f};
    bool alarm_triggered{false};
};

class ElectrostaticFieldMeter {
public:
    explicit ElectrostaticFieldMeter(std::uint8_t i2c_addr, FieldRange range) noexcept
        : addr_(i2c_addr), range_(range) {}

    [[nodiscard]] std::expected<void, DriverError> initialize() noexcept {
        const std::uint8_t dev_id = read_reg(0x00);
        if (dev_id != 0xE5) {
            return std::unexpected(DriverError::InvalidDeviceID);
        }
        write_reg(0x02, static_cast<std::uint8_t>(range_));
        write_reg(0x01, 0x11); // EN_MOD = 1, Continuous Mode
        return {};
    }

    [[nodiscard]] std::expected<FieldData, DriverError> read_field() const noexcept {
        const std::uint8_t status = read_reg(0x04);
        if (status & 0x04) {
            return std::unexpected(DriverError::DeviceSaturated);
        }

        const std::uint8_t raw_h = read_reg(0x06);
        const std::uint8_t raw_l = read_reg(0x07);
        const auto raw_16 = static_cast<std::int16_t>((raw_h << 8) | raw_l);

        const float lsb_scale = get_scale_factor(range_);
        FieldData data;
        data.field_kv_per_m = static_cast<float>(raw_16) * lsb_scale;
        data.induced_charge_nc = data.field_kv_per_m * kSensorCapacitance_nF;
        data.alarm_triggered = (status & 0x02) != 0;

        return data;
    }

private:
    std::uint8_t addr_;
    FieldRange range_;
    static constexpr float kSensorCapacitance_nF = 0.012f;

    [[nodiscard]] static float get_scale_factor(FieldRange r) noexcept {
        switch (r) {
            case FieldRange::Range1kV:   return 0.000030517f; // 1 кВ / 32768
            case FieldRange::Range5kV:   return 0.000152587f;
            case FieldRange::Range20kV:  return 0.000610351f;
            case FieldRange::Range100kV: return 0.003051757f;
        }
        return 0.000030517f;
    }

    [[nodiscard]] std::uint8_t read_reg(std::uint8_t reg) const noexcept {
        return (reg == 0x00) ? 0xE5 : 0x00;
    }

    void write_reg(std::uint8_t reg, std::uint8_t val) const noexcept {
        (void)reg; (void)val;
    }
};

} // namespace esm

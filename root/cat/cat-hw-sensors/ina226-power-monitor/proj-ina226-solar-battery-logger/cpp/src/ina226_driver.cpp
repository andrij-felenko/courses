#include "ina226_driver.hpp"
#include <cmath>
#include <iostream>

namespace power_monitor {

Ina226Driver::Ina226Driver(I2CBus& bus, uint8_t dev_addr)
    : bus_(bus), dev_addr_(dev_addr) {}

bool Ina226Driver::write_reg(uint8_t reg, uint16_t val) {
    return bus_.write_register(dev_addr_, reg, val);
}

bool Ina226Driver::read_reg(uint8_t reg, uint16_t& val) {
    return bus_.read_register(dev_addr_, reg, val);
}

bool Ina226Driver::soft_reset() {
    constexpr uint16_t RESET_BIT = 1U << 15;
    if (!write_reg(REG_CONFIG, RESET_BIT)) {
        return false;
    }
    config_cache_ = 0x4127;
    is_sleeping_ = false;
    return true;
}

bool Ina226Driver::verify_device_id() {
    uint16_t mfg_id = 0;
    uint16_t die_id = 0;

    if (!read_reg(REG_MANUFACTURER_ID, mfg_id) || !read_reg(REG_DIE_ID, die_id)) {
        return false;
    }

    return (mfg_id == EXPECTED_MANUFACTURER_ID) && ((die_id & 0xFFF0) == (EXPECTED_DIE_ID & 0xFFF0));
}

bool Ina226Driver::begin(double r_shunt_ohms, double max_expected_current_a) {
    if (!verify_device_id()) {
        std::cerr << "[INA226 Driver] Помилка: невірний ID пристрою або збій шини I2C.\n";
        return false;
    }

    if (!soft_reset()) {
        std::cerr << "[INA226 Driver] Помилка виконання Soft Reset.\n";
        return false;
    }

    if (!calibrate(r_shunt_ohms, max_expected_current_a)) {
        std::cerr << "[INA226 Driver] Помилка обчислення та запису регістра Calibration.\n";
        return false;
    }

    return configure(Averaging::AVG_16, ConversionTime::TIME_1100US, ConversionTime::TIME_1100US, OperatingMode::SHUNT_BUS_CONTINUOUS);
}

bool Ina226Driver::calibrate(double r_shunt_ohms, double max_expected_current_a) {
    if (r_shunt_ohms <= 0.0 || max_expected_current_a <= 0.0) {
        return false;
    }

    // 1. Початковий розрахунок Current_LSB
    // Знаковий 16-бітний регістр має максимальний діапазон 32768 одиниць
    current_lsb_ = max_expected_current_a / 32768.0;

    // 2. Формула специфікації INA226: CAL = floor(0.00512 / (Current_LSB * R_shunt))
    // 0.00512 — це внутрішня константа масштабування INA226
    double cal_exact = 0.00512 / (current_lsb_ * r_shunt_ohms);
    if (cal_exact > 65535.0) {
        cal_exact = 65535.0; // Обмеження 16-бітного регістра
    }

    calibration_val_ = static_cast<uint16_t>(std::floor(cal_exact));
    if (calibration_val_ == 0) {
        return false;
    }

    // 3. Точний перерахунок Current_LSB на основі дискретизованого CAL
    current_lsb_ = 0.00512 / (static_cast<double>(calibration_val_) * r_shunt_ohms);

    // 4. Power_LSB фіксовано дорівнює 25 * Current_LSB
    power_lsb_ = 25.0 * current_lsb_;

    // 5. Запис у регістр Calibration (0x05)
    return write_reg(REG_CALIBRATION, calibration_val_);
}

bool Ina226Driver::set_calibration_raw(uint16_t cal_val, double current_lsb) {
    calibration_val_ = cal_val;
    current_lsb_ = current_lsb;
    power_lsb_ = 25.0 * current_lsb_;
    return write_reg(REG_CALIBRATION, calibration_val_);
}

bool Ina226Driver::configure(Averaging avg, ConversionTime vbus_ct, ConversionTime vsh_ct, OperatingMode mode) {
    uint16_t config = static_cast<uint16_t>(avg) |
                      (static_cast<uint16_t>(vbus_ct) << 6) |
                      (static_cast<uint16_t>(vsh_ct) << 3) |
                      static_cast<uint16_t>(mode);

    if (write_reg(REG_CONFIG, config)) {
        config_cache_ = config;
        is_sleeping_ = (mode == OperatingMode::POWER_DOWN || mode == OperatingMode::POWER_DOWN_ALT);
        return true;
    }
    return false;
}

bool Ina226Driver::read_bus_voltage(double& bus_voltage_v) {
    uint16_t raw = 0;
    if (!read_reg(REG_BUS_VOLTAGE, raw)) {
        return false;
    }
    // LSB напруги шини = 1.25 мВ = 0.00125 В
    bus_voltage_v = static_cast<double>(raw) * 0.00125;
    return true;
}

bool Ina226Driver::read_shunt_voltage(double& shunt_voltage_mv) {
    uint16_t raw = 0;
    if (!read_reg(REG_SHUNT_VOLTAGE, raw)) {
        return false;
    }
    // Перетворення 16-бітного знакового значення (2's complement)
    int16_t signed_raw = static_cast<int16_t>(raw);
    // LSB напруги шунта = 2.5 мкВ = 0.0025 мВ
    shunt_voltage_mv = static_cast<double>(signed_raw) * 0.0025;
    return true;
}

bool Ina226Driver::read_current(double& current_a) {
    uint16_t raw = 0;
    if (!read_reg(REG_CURRENT, raw)) {
        return false;
    }
    // Перетворення 16-бітного знакового значення (2's complement):
    // додатне значення означає струм заряду, від'ємне — струм розряду.
    int16_t signed_raw = static_cast<int16_t>(raw);
    current_a = static_cast<double>(signed_raw) * current_lsb_;
    return true;
}

bool Ina226Driver::read_power(double& power_w) {
    uint16_t raw = 0;
    if (!read_reg(REG_POWER, raw)) {
        return false;
    }
    // Регістр потужності в INA226 є беззнаковим (модуль миттєвої потужності)
    power_w = static_cast<double>(raw) * power_lsb_;
    return true;
}

bool Ina226Driver::read_all(double& bus_voltage_v, double& current_a, double& power_w) {
    bool status = read_bus_voltage(bus_voltage_v);
    status = status && read_current(current_a);
    status = status && read_power(power_w);
    return status;
}

bool Ina226Driver::set_sleep_mode(bool sleep) {
    if (sleep == is_sleeping_) {
        return true;
    }

    if (sleep) {
        // Переведення в Power-Down (маска 0b000 у бітах 2-0)
        uint16_t sleep_config = (config_cache_ & ~0x0007) | static_cast<uint16_t>(OperatingMode::POWER_DOWN);
        if (write_reg(REG_CONFIG, sleep_config)) {
            is_sleeping_ = true;
            return true;
        }
    } else {
        // Відновлення робочої конфігурації
        if (write_reg(REG_CONFIG, config_cache_)) {
            is_sleeping_ = false;
            return true;
        }
    }
    return false;
}

} // namespace power_monitor

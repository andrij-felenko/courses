#include "sccb_bus.hpp"
#include <iostream>

namespace camera {

constexpr uint8_t REG_BANK_SEL = 0xFF;
constexpr uint8_t REG_PID_LOW  = 0x0A;
constexpr uint8_t REG_VER_LOW  = 0x0B;
constexpr uint16_t OV3640_EXPECTED_ID = 0x3640;

SccbBus::SccbBus(uint8_t device_address)
    : device_address_(device_address) {}

bool SccbBus::init() {
    // Симуляція ініціалізації периферії I2C/SCCB на мікроконтролері
    initialized_ = true;
    current_bank_ = 0xFF; // Скидаємо збережений банк
    return true;
}

bool SccbBus::select_bank(uint8_t bank) {
    if (!initialized_) {
        return false;
    }
    // Якщо банк вже обрано, уникаємо зайвих транзакцій по шині
    if (current_bank_ == bank) {
        return true;
    }

    if (i2c_transmit(REG_BANK_SEL, bank)) {
        current_bank_ = bank;
        return true;
    }
    return false;
}

bool SccbBus::write_register(uint8_t reg, uint8_t value) {
    if (!initialized_) {
        return false;
    }
    return i2c_transmit(reg, value);
}

bool SccbBus::read_register(uint8_t reg, uint8_t& value) {
    if (!initialized_) {
        return false;
    }
    return i2c_receive(reg, value);
}

bool SccbBus::write_bank_register(uint8_t bank, uint8_t reg, uint8_t value) {
    if (!select_bank(bank)) {
        return false;
    }
    return write_register(reg, value);
}

bool SccbBus::read_bank_register(uint8_t bank, uint8_t reg, uint8_t& value) {
    if (!select_bank(bank)) {
        return false;
    }
    return read_register(reg, value);
}

bool SccbBus::verify_sensor_id(uint16_t& sensor_id) {
    sensor_id = 0;
    uint8_t pid_val = 0;
    uint8_t ver_val = 0;

    // Зчитуємо ідентифікаційні регістри PID та VER (банк 0)
    if (!read_bank_register(0x00, REG_PID_LOW, pid_val)) {
        return false;
    }
    if (!read_bank_register(0x00, REG_VER_LOW, ver_val)) {
        return false;
    }

    sensor_id = static_cast<uint16_t>((pid_val << 8) | ver_val);
    return (sensor_id == OV3640_EXPECTED_ID);
}

bool SccbBus::write_register_list(uint8_t bank, const std::vector<std::pair<uint8_t, uint8_t>>& reg_list) {
    if (!select_bank(bank)) {
        return false;
    }
    for (const auto& [reg, val] : reg_list) {
        if (!write_register(reg, val)) {
            return false;
        }
    }
    return true;
}

bool SccbBus::i2c_transmit(uint8_t reg, uint8_t val) {
    // Емуляція апаратного трансивера SCCB
    // На реальному МК тут викликається HAL_I2C_Master_Transmit / I2C_Transfer
    return true;
}

bool SccbBus::i2c_receive(uint8_t reg, uint8_t& val) {
    // Емуляція зчитування з SCCB
    if (reg == REG_PID_LOW) {
        val = 0x36; // PID OV3640
    } else if (reg == REG_VER_LOW) {
        val = 0x40; // VER OV3640
    } else {
        val = 0x00;
    }
    return true;
}

} // namespace camera

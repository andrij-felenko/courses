#include "sccb_bus.hpp"
#include "ov2640_registers.hpp"
#include <iostream>
#include <thread>
#include <chrono>

namespace ov2640 {

SccbBus::SccbBus(uint8_t device_address)
    : device_address_(device_address),
      current_bank_(RegisterBank::DSP),
      is_initialized_(false) {}

SccbStatus SccbBus::init() {
    // Імітація ініціалізації контролера I2C/SCCB периферії мікроконтролера
    is_initialized_ = true;
    current_bank_ = RegisterBank::DSP;
    
    // Перевіряємо доступність шини записом адреси банку за замовчуванням
    return selectBank(RegisterBank::DSP);
}

SccbStatus SccbBus::selectBank(RegisterBank bank) {
    if (!is_initialized_) {
        return SccbStatus::ErrNotInitialized;
    }

    // Якщо банк вже вибрано, повторний запис на шину не виконуємо для оптимізації
    if (bank == current_bank_) {
        return SccbStatus::Ok;
    }

    uint8_t bank_val = static_cast<uint8_t>(bank);
    SccbStatus status = lowLevelWrite(REG_BANK_SEL, bank_val);
    if (status == SccbStatus::Ok) {
        current_bank_ = bank;
    }
    return status;
}

SccbStatus SccbBus::writeRegister(uint8_t reg, uint8_t value) {
    if (!is_initialized_) {
        return SccbStatus::ErrNotInitialized;
    }
    return lowLevelWrite(reg, value);
}

SccbStatus SccbBus::readRegister(uint8_t reg, uint8_t& out_value) {
    if (!is_initialized_) {
        return SccbStatus::ErrNotInitialized;
    }
    return lowLevelRead(reg, out_value);
}

SccbStatus SccbBus::writeRegisterList(const uint8_t reg_pairs[][2], size_t count) {
    if (!is_initialized_) {
        return SccbStatus::ErrNotInitialized;
    }

    for (size_t i = 0; i < count; ++i) {
        uint8_t reg = reg_pairs[i][0];
        uint8_t val = reg_pairs[i][1];

        // Якщо регістр є селектором банку 0xFF, оновлюємо стан внутрішнього банку
        if (reg == REG_BANK_SEL) {
            SccbStatus status = selectBank(static_cast<RegisterBank>(val));
            if (status != SccbStatus::Ok) {
                return status;
            }
        } else {
            SccbStatus status = writeRegister(reg, val);
            if (status != SccbStatus::Ok) {
                return status;
            }
        }
    }
    return SccbStatus::Ok;
}

SccbStatus SccbBus::verifyDeviceId(uint8_t& out_pid, uint8_t& out_ver) {
    // Ідентифікаційні регістри розміщені у банку Sensor (0x01)
    SccbStatus status = selectBank(RegisterBank::Sensor);
    if (status != SccbStatus::Ok) {
        return status;
    }

    status = readRegister(REG_SENSOR_PID, out_pid);
    if (status != SccbStatus::Ok) {
        return status;
    }

    status = readRegister(REG_SENSOR_VER, out_ver);
    if (status != SccbStatus::Ok) {
        return status;
    }

    if (out_pid != OV2640_EXPECTED_PID || out_ver != OV2640_EXPECTED_VER) {
        return SccbStatus::ErrBusHardware;
    }

    return SccbStatus::Ok;
}

SccbStatus SccbBus::lowLevelWrite(uint8_t reg, uint8_t val) {
    // Симуляція транзакції SCCB Write: [START] -> [Addr+W] -> [Reg] -> [Val] -> [STOP]
    (void)reg;
    (void)val;
    return SccbStatus::Ok;
}

SccbStatus SccbBus::lowLevelRead(uint8_t reg, uint8_t& val) {
    // Симуляція транзакції SCCB Read: 
    // 1. [START] -> [Addr+W] -> [Reg] -> [STOP]
    // 2. [START] -> [Addr+R] -> [Data] -> [NACK] -> [STOP]
    if (reg == REG_SENSOR_PID) {
        val = OV2640_EXPECTED_PID; // 0x26
    } else if (reg == REG_SENSOR_VER) {
        val = OV2640_EXPECTED_VER; // 0x42
    } else if (reg == REG_SENSOR_MIDH) {
        val = 0x7F;
    } else if (reg == REG_SENSOR_MIDL) {
        val = 0xA2;
    } else {
        val = 0x00;
    }
    return SccbStatus::Ok;
}

} // namespace ov2640

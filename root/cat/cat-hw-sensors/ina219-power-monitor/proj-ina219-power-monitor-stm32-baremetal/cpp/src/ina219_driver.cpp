#include "ina219_driver.hpp"

namespace ina219 {

// -----------------------------------------------------------------------------
// Реалізація RAII-обгортки I2cBusGuard
// -----------------------------------------------------------------------------

I2cBusGuard::I2cBusGuard(I2C_HandleTypeDef* hi2c, uint16_t dev_addr, uint32_t timeout_ms)
    : hi2c_(hi2c), dev_addr_(dev_addr), timeout_ms_(timeout_ms), last_status_(HAL_OK), active_(true) {}

I2cBusGuard::~I2cBusGuard() {
    if (active_ && last_status_ != HAL_OK) {
        recoverBus();
    }
}

I2cBusGuard::I2cBusGuard(I2cBusGuard&& other) noexcept
    : hi2c_(other.hi2c_),
      dev_addr_(other.dev_addr_),
      timeout_ms_(other.timeout_ms_),
      last_status_(other.last_status_),
      active_(other.active_) {
    other.active_ = false;
}

I2cBusGuard& I2cBusGuard::operator=(I2cBusGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && last_status_ != HAL_OK) {
            recoverBus();
        }
        hi2c_ = other.hi2c_;
        dev_addr_ = other.dev_addr_;
        timeout_ms_ = other.timeout_ms_;
        last_status_ = other.last_status_;
        active_ = other.active_;
        other.active_ = false;
    }
    return *this;
}

void I2cBusGuard::recoverBus() {
    if (!hi2c_) return;

#if defined(HAL_I2C_MODULE_ENABLED) || defined(STM32F4xx_HAL_H)
    // Апаратна перезавантаження інтерфейсу I2C для усунення заклинювання шини
    HAL_I2C_DeInit(hi2c_);
    HAL_I2C_Init(hi2c_);
#endif
}

HAL_StatusTypeDef I2cBusGuard::writeRegister(uint8_t reg_addr, uint16_t value) {
    if (!hi2c_) {
        last_status_ = HAL_ERROR;
        return last_status_;
    }

    uint8_t buffer[2];
    buffer[0] = static_cast<uint8_t>((value >> 8) & 0xFF);
    buffer[1] = static_cast<uint8_t>(value & 0xFF);

#if defined(HAL_I2C_MODULE_ENABLED) || defined(STM32F4xx_HAL_H)
    last_status_ = HAL_I2C_Mem_Write(hi2c_, dev_addr_, reg_addr, I2C_MEMADD_SIZE_8BIT, buffer, 2, timeout_ms_);
#else
    (void)reg_addr;
    (void)buffer;
    last_status_ = HAL_OK;
#endif

    if (last_status_ != HAL_OK) {
        recoverBus();
    }
    return last_status_;
}

HAL_StatusTypeDef I2cBusGuard::readRegister(uint8_t reg_addr, uint16_t& value) {
    if (!hi2c_) {
        last_status_ = HAL_ERROR;
        return last_status_;
    }

    uint8_t buffer[2] = {0, 0};

#if defined(HAL_I2C_MODULE_ENABLED) || defined(STM32F4xx_HAL_H)
    last_status_ = HAL_I2C_Mem_Read(hi2c_, dev_addr_, reg_addr, I2C_MEMADD_SIZE_8BIT, buffer, 2, timeout_ms_);
#else
    (void)reg_addr;
    last_status_ = HAL_OK;
#endif

    if (last_status_ == HAL_OK) {
        value = static_cast<uint16_t>((static_cast<uint16_t>(buffer[0]) << 8) | buffer[1]);
    } else {
        recoverBus();
    }
    return last_status_;
}

// -----------------------------------------------------------------------------
// Реалізація драйвера Ina219Driver
// -----------------------------------------------------------------------------

Ina219Driver::Ina219Driver(I2C_HandleTypeDef* hi2c, uint8_t i2c_addr)
    : hi2c_(hi2c), i2c_addr_shifted_(static_cast<uint16_t>(i2c_addr << 1)) {}

HAL_StatusTypeDef Ina219Driver::init(float r_shunt_ohms, float max_current_A) {
    if (!hi2c_) {
        return HAL_ERROR;
    }

    // 1. Програмне скидання сенсора
    HAL_StatusTypeDef status = reset();
    if (status != HAL_OK) {
        return status;
    }

    // 2. Обчислення і запис калібрування
    status = calibrate(r_shunt_ohms, max_current_A);
    if (status != HAL_OK) {
        return status;
    }

    // 3. Застосування базової конфігурації
    return configure();
}

HAL_StatusTypeDef Ina219Driver::reset() {
    HAL_StatusTypeDef status = writeRegister(Ina219Register::Config, kConfigResetMask);
    if (status == HAL_OK) {
        config_reg_val_ = 0x399F; // Замовчуване значення конфігурації INA219
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::configure(
    Ina219BusVoltageRange bus_range,
    Ina219PgaGain gain,
    Ina219AdcResolution bus_adc,
    Ina219AdcResolution shunt_adc,
    Ina219Mode mode
) {
    config_reg_val_ = static_cast<uint16_t>(bus_range) |
                      static_cast<uint16_t>(gain) |
                      static_cast<uint16_t>(bus_adc) |
                      static_cast<uint16_t>(shunt_adc) |
                      static_cast<uint16_t>(mode);

    return writeRegister(Ina219Register::Config, config_reg_val_);
}

void Ina219Driver::calculateLsbAndCal() {
    // 1. Current LSB (Ампер/бітно): I_max / 32768
    current_lsb_A_ = max_current_A_ / 32768.0f;

    // 2. Power LSB (Ват/бітно): 20 * Current LSB
    power_lsb_W_ = 20.0f * current_lsb_A_;

    // 3. Calibration Register value:
    // Cal = trunc(0.04096 / (Current_LSB * R_shunt))
    if (current_lsb_A_ > 0.0f && r_shunt_ohms_ > 0.0f) {
        float cal_float = 0.04096f / (current_lsb_A_ * r_shunt_ohms_);
        cal_reg_val_ = static_cast<uint16_t>(std::trunc(cal_float));
    } else {
        cal_reg_val_ = 0;
    }
}

HAL_StatusTypeDef Ina219Driver::calibrate(float r_shunt_ohms, float max_current_A) {
    if (r_shunt_ohms <= 0.0f || max_current_A <= 0.0f) {
        return HAL_ERROR;
    }

    r_shunt_ohms_ = r_shunt_ohms;
    max_current_A_ = max_current_A;

    calculateLsbAndCal();

    return writeRegister(Ina219Register::Calibration, cal_reg_val_);
}

HAL_StatusTypeDef Ina219Driver::readShuntVoltage(float& voltage_mV) {
    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::ShuntVoltage, raw_val);
    if (status == HAL_OK) {
        // Знакове 16-бітне значення. 1 LSB = 10 мкВ = 0.01 мВ
        int16_t raw_signed = static_cast<int16_t>(raw_val);
        voltage_mV = static_cast<float>(raw_signed) * 0.01f;
    } else {
        voltage_mV = 0.0f;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::readBusVoltage(float& voltage_V) {
    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::BusVoltage, raw_val);
    if (status == HAL_OK) {
        // Біти 15..3 представляють значення напруги шини. 1 LSB = 4 мВ = 0.004 В
        int16_t bus_raw = static_cast<int16_t>((raw_val >> 3) & 0x1FFF);
        voltage_V = static_cast<float>(bus_raw) * 0.004f;
    } else {
        voltage_V = 0.0f;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::readCurrent(float& current_mA) {
    // Підтвердження запису коефіцієнта калібрування перед зчитуванням обчисленого струму
    writeRegister(Ina219Register::Calibration, cal_reg_val_);

    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::Current, raw_val);
    if (status == HAL_OK) {
        int16_t current_signed = static_cast<int16_t>(raw_val);
        current_mA = static_cast<float>(current_signed) * (current_lsb_A_ * 1000.0f);
    } else {
        current_mA = 0.0f;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::readPower(float& power_mW) {
    // Підтвердження запису калібрування перед зчитуванням потужності
    writeRegister(Ina219Register::Calibration, cal_reg_val_);

    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::Power, raw_val);
    if (status == HAL_OK) {
        power_mW = static_cast<float>(raw_val) * (power_lsb_W_ * 1000.0f);
    } else {
        power_mW = 0.0f;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::readAll(float& bus_voltage_V, float& shunt_voltage_mV, float& current_mA, float& power_mW) {
    HAL_StatusTypeDef status = readBusVoltage(bus_voltage_V);
    if (status != HAL_OK) return status;

    status = readShuntVoltage(shunt_voltage_mV);
    if (status != HAL_OK) return status;

    status = readCurrent(current_mA);
    if (status != HAL_OK) return status;

    status = readPower(power_mW);
    return status;
}

HAL_StatusTypeDef Ina219Driver::checkConversionReady(bool& is_ready) {
    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::BusVoltage, raw_val);
    if (status == HAL_OK) {
        // CNVR — Біт 1 в регістрі Bus Voltage
        is_ready = (raw_val & kBusVoltageCnvrMask) != 0;
    } else {
        is_ready = false;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::checkOverflow(bool& is_overflow) {
    uint16_t raw_val = 0;
    HAL_StatusTypeDef status = readRegister(Ina219Register::BusVoltage, raw_val);
    if (status == HAL_OK) {
        // OVF — Біт 0 в регістрі Bus Voltage
        is_overflow = (raw_val & kBusVoltageOvfMask) != 0;
    } else {
        is_overflow = false;
    }
    return status;
}

HAL_StatusTypeDef Ina219Driver::writeRegister(Ina219Register reg, uint16_t value) {
    I2cBusGuard guard(hi2c_, i2c_addr_shifted_);
    return guard.writeRegister(static_cast<uint8_t>(reg), value);
}

HAL_StatusTypeDef Ina219Driver::readRegister(Ina219Register reg, uint16_t& value) {
    I2cBusGuard guard(hi2c_, i2c_addr_shifted_);
    return guard.readRegister(static_cast<uint8_t>(reg), value);
}

} // namespace ina219

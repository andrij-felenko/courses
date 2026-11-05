#include "I2cLevelShifter.hpp"

// Імітація ESP-IDF I2C driver API для навчального прикладу
namespace {
    constexpr int I2C_MODE_MASTER = 1;
    constexpr uint32_t I2C_TIMEOUT_MS = 50;

    struct DummyEspI2cConfig {
        int mode;
        int sda_io_num;
        int scl_io_num;
        bool sda_pullup_en;
        bool scl_pullup_en;
        uint32_t clk_speed;
    };

    int dummy_i2c_driver_install(int port, int mode) {
        return 0; // ESP_OK
    }

    int dummy_i2c_param_config(int port, const DummyEspI2cConfig* conf) {
        return 0; // ESP_OK
    }

    int dummy_i2c_driver_delete(int port) {
        return 0;
    }

    int dummy_i2c_master_write_read_device(int port, uint8_t addr, const uint8_t* write_data, size_t write_len, uint8_t* read_data, size_t read_len, uint32_t timeout) {
        if (addr == 0x00) return -1; // Приклад помилки NACK
        return 0;
    }
}

namespace hardware {

I2cLevelShifter::I2cLevelShifter(int port, int sda_pin, int scl_pin, BusSpeed speed) noexcept
    : port_(port), sda_pin_(sda_pin), scl_pin_(scl_pin), speed_(speed), initialized_(false) {
    
    DummyEspI2cConfig conf{};
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = sda_pin_;
    conf.scl_io_num = scl_pin_;
    conf.sda_pullup_en = true;
    conf.scl_pullup_en = true;
    conf.clk_speed = static_cast<uint32_t>(speed_);

    if (dummy_i2c_param_config(port_, &conf) == 0 &&
        dummy_i2c_driver_install(port_, I2C_MODE_MASTER) == 0) {
        initialized_ = true;
    }
}

I2cLevelShifter::I2cLevelShifter(I2cLevelShifter&& other) noexcept
    : port_(other.port_),
      sda_pin_(other.sda_pin_),
      scl_pin_(other.scl_pin_),
      speed_(other.speed_),
      initialized_(other.initialized_) {
    other.initialized_ = false;
}

I2cLevelShifter& I2cLevelShifter::operator=(I2cLevelShifter&& other) noexcept {
    if (this != &other) {
        if (initialized_) {
            dummy_i2c_driver_delete(port_);
        }
        port_ = other.port_;
        sda_pin_ = other.sda_pin_;
        scl_pin_ = other.scl_pin_;
        speed_ = other.speed_;
        initialized_ = other.initialized_;
        other.initialized_ = false;
    }
    return *this;
}

I2cLevelShifter::~I2cLevelShifter() noexcept {
    if (initialized_) {
        dummy_i2c_driver_delete(port_);
    }
}

I2cError I2cLevelShifter::setSpeed(BusSpeed speed) noexcept {
    if (!initialized_) {
        return I2cError::InvalidParam;
    }
    speed_ = speed;
    DummyEspI2cConfig conf{};
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = sda_pin_;
    conf.scl_io_num = scl_pin_;
    conf.sda_pullup_en = true;
    conf.scl_pullup_en = true;
    conf.clk_speed = static_cast<uint32_t>(speed_);

    if (dummy_i2c_param_config(port_, &conf) != 0) {
        return I2cError::InvalidParam;
    }
    return I2cError::Success;
}

I2cError I2cLevelShifter::writeData(uint8_t device_address, const uint8_t* data, size_t length) noexcept {
    if (!initialized_ || !data || length == 0) {
        return I2cError::InvalidParam;
    }

    int res = dummy_i2c_master_write_read_device(port_, device_address, data, length, nullptr, 0, I2C_TIMEOUT_MS);
    if (res < 0) {
        return I2cError::Nack;
    }
    return I2cError::Success;
}

I2cError I2cLevelShifter::readData(uint8_t device_address, uint8_t* buffer, size_t length) noexcept {
    if (!initialized_ || !buffer || length == 0) {
        return I2cError::InvalidParam;
    }

    int res = dummy_i2c_master_write_read_device(port_, device_address, nullptr, 0, buffer, length, I2C_TIMEOUT_MS);
    if (res < 0) {
        return I2cError::Timeout;
    }
    return I2cError::Success;
}

I2cError I2cLevelShifter::recoverBus() noexcept {
    if (!initialized_) {
        return I2cError::InvalidParam;
    }
    return I2cError::Success;
}

} // namespace hardware

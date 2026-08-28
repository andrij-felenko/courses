/* i2c_driver.cpp - Приватний файл реалізації C++20 */
#include "i2c_driver.hpp"

namespace driver {

struct I2cPort::Impl {
    std::uintptr_t hw_base{0};
    uint32_t clock_hz{100'000};
    uint16_t timeout{50};
    volatile uint32_t state{0};
};

static I2cPort::Impl s_cpp_instances[2];

I2cPort::I2cPort(uint8_t port_index, const I2cConfig& config) noexcept {
    if (port_index < 2) {
        pimpl_ = &s_cpp_instances[port_index];
        pimpl_->hw_base = (port_index == 0) ? 0x40005400 : 0x40005800;
    }
}

I2cPort::~I2cPort() noexcept = default;

} // namespace driver

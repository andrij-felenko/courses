// hal/hal_i2c.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class I2cError {
    Nack,
    BusError,
    Timeout
};

class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual std::expected<void, I2cError> mem_read(uint8_t dev_addr, uint8_t reg_addr, 
                                                   std::span<uint8_t> data) = 0;
    virtual std::expected<void, I2cError> mem_write(uint8_t dev_addr, uint8_t reg_addr, 
                                                    std::span<const uint8_t> data) = 0;
};

} // namespace hal

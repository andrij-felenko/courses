// hal/hal_i2c.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class I2cError : uint8_t {
    Nack,
    Timeout,
    BusFailure
};

// Чисто віртуальний інтерфейс шини I2C
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual std::expected<void, I2cError> write_reg(uint8_t dev_addr, uint8_t reg_addr, 
                                                    std::span<const uint8_t> data) = 0;
    virtual std::expected<void, I2cError> read_reg(uint8_t dev_addr, uint8_t reg_addr, 
                                                   std::span<uint8_t> data) = 0;
};

} // namespace hal

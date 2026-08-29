// hal/hal_i2c.hpp — контракт шини I2C.
// std::span несе довжину разом із покажчиком, тому вийти за межі буфера
// драйвер просто не має чим; std::expected прибирає мовчазні коди повернення.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace hal {

enum class I2cError : std::uint8_t {
    Nack,        // Пристрій не підтвердив адресу або байт
    Timeout,     // Ліміт очікування прапорця вичерпано
    BusFailure,  // Арбітраж програно, лінію притиснуто, помилка кадру
};

class II2cBus {
public:
    virtual ~II2cBus() = default;

    II2cBus() = default;
    II2cBus(const II2cBus&) = delete;
    II2cBus& operator=(const II2cBus&) = delete;

    virtual std::expected<void, I2cError> write_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                    std::span<const std::uint8_t> data) = 0;

    virtual std::expected<void, I2cError> read_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                   std::span<std::uint8_t> data) = 0;

    // Зручність, яку не варто повторювати в кожному драйвері.
    std::expected<void, I2cError> write_u8(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                           std::uint8_t value)
    {
        const std::uint8_t one[1]{value};
        return write_reg(dev_addr, reg_addr, one);
    }
};

}  // namespace hal

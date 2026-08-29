// Шина очима драйвера: два обміни байтами й нічого більше. Часом розпоряджається
// сам сеанс, тому виклику затримки тут немає — на відміну від сішного HAL.
#pragma once

#include <cstdint>
#include <span>

namespace atecc {

class I2cBus {
public:
    virtual ~I2cBus() = default;

    I2cBus(const I2cBus&) = delete;
    I2cBus& operator=(const I2cBus&) = delete;

    // false означає лише «пристрій не підтвердив адресу»: для крипточипа це
    // штатна відповідь «обчислення ще триває», а не аварія.
    [[nodiscard]] virtual bool write(std::uint8_t address, std::span<const std::uint8_t> data) = 0;
    [[nodiscard]] virtual bool read(std::uint8_t address, std::span<std::uint8_t> data) = 0;

protected:
    I2cBus() = default;
};

} // namespace atecc

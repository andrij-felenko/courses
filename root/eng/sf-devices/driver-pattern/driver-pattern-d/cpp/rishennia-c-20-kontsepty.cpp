#include <concepts>
#include <span>
#include <cstdint>

namespace driver {

/* Адаптер I2C на C++20 без єдиного віртуального виклику */
class I2cBusAdapter {
public:
    explicit I2cBusAdapter(I2cDriver& driver) noexcept : driver_(driver) {}

    Status write_reg(uint8_t dev_addr, uint8_t reg_addr, std::span<const uint8_t> data) noexcept {
        uint8_t buffer[33];
        if (data.size() > 32) return Status::InvalidParam;
        buffer[0] = reg_addr;
        for (size_t i = 0; i < data.size(); ++i) {
            buffer[i + 1] = data[i];
        }
        auto res = driver_.master_write(dev_addr, std::span<const uint8_t>(buffer, data.size() + 1));
        return res.has_value() ? Status::Ok : res.error();
    }

    Status read_reg(uint8_t dev_addr, uint8_t reg_addr, std::span<uint8_t> data) noexcept {
        // Логіка читання регістра
        (void)dev_addr; (void)reg_addr; (void)data;
        return Status::Ok;
    }

private:
    I2cDriver& driver_;
};

// Перевірка відповідності концепту під час компіляції
static_assert(BusDevice<I2cBusAdapter>, "I2cBusAdapter must satisfy BusDevice concept");

} // namespace driver

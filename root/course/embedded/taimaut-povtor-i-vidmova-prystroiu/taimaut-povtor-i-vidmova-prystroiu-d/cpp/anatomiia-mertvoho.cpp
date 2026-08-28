#include <cstdint>

// Смертельна пастка у стилі C++: блокуюче опитування регістрів без дедлайну
struct I2cRegisters {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
    volatile uint32_t DR;
};

void i2c_write_byte_naive(I2cRegisters* i2c, uint8_t data) noexcept {
    i2c->DR = data;
    constexpr uint32_t TXE_FLAG = (1UL << 7);
    constexpr uint32_t BTF_FLAG = (1UL << 2);

    while ((i2c->SR1 & TXE_FLAG) == 0) {
        // Очікування без дедлайну блокує потік назавжди
    }
    while ((i2c->SR1 & BTF_FLAG) == 0) {
        // Зависання при відриві SCL або утриманні лінії веденим чипом
    }
}

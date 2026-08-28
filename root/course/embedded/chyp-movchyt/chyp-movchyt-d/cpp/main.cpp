/* Базовий алгоритм сканування шини I2C (Сучасний C++ / Embedded HAL) */
#include <cstdint>
#include <cstdio>
#include <span>
#include <concepts>

template <typename I2CDeviceChecker>
concept DeviceChecker = requires(I2CDeviceChecker checker, std::uint8_t addr_7bit) {
    { checker.is_ready(addr_7bit) } -> std::same_as<bool>;
};

template <DeviceChecker Checker>
void scan_i2c_bus(Checker& checker) {
    std::printf("\r\n--- Сканування простору 7-бітних адрес I2C (C++) ---\r\n");
    std::size_t found_count = 0;

    for (std::uint8_t addr = 0x08; addr <= 0x77; ++addr) {
        if (checker.is_ready(addr)) {
            std::printf("Пристрій знайдено: 7-bit = 0x%02X, 8-bit WR = 0x%02X\r\n",
                        addr, static_cast<std::uint8_t>(addr << 1));
            ++found_count;
        }
    }

    if (found_count == 0) {
        std::printf("Помилка: на шині тиша. Перевірте апаратні лінії.\r\n");
    } else {
        std::printf("Успішно знайдено пристроїв: %zu\r\n", found_count);
    }
}

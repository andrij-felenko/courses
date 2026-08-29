// Втілення шини для Linux: /dev/i2c-N через ioctl I2C_RDWR. Дескриптор
// закриває деструктор — окремої функції close тут немає.
#pragma once

#include <string_view>

#include "i2c_bus.hpp"

namespace atecc {

class LinuxI2cBus final : public I2cBus {
public:
    // Кидає std::system_error, якщо шину не вдалося відкрити: це помилка
    // налаштування, а не робочий стан драйвера.
    explicit LinuxI2cBus(std::string_view devicePath);
    ~LinuxI2cBus() override;

    LinuxI2cBus(LinuxI2cBus&& other) noexcept;
    LinuxI2cBus& operator=(LinuxI2cBus&& other) noexcept;

    [[nodiscard]] bool write(std::uint8_t address, std::span<const std::uint8_t> data) override;
    [[nodiscard]] bool read(std::uint8_t address, std::span<std::uint8_t> data) override;

private:
    int fd_ = -1;
};

} // namespace atecc

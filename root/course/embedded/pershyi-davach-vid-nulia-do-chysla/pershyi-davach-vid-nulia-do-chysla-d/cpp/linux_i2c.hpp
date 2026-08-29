#pragma once

/* Шина I2C через драйвер i2c-dev ядра Linux (/dev/i2c-N).
   Дескриптор живе рівно стільки, скільки об'єкт: закриває його деструктор,
   тому жодних гілок «закрити перед виходом» у коді драйвера немає. */

#include <cstdint>
#include <span>
#include <string>

namespace sht3x {

class LinuxI2c {
public:
    // Кидає std::system_error, якщо шини немає або адресу зайняв інший драйвер.
    LinuxI2c(const std::string& bus_path, std::uint8_t address7);
    ~LinuxI2c();

    LinuxI2c(const LinuxI2c&)            = delete;
    LinuxI2c& operator=(const LinuxI2c&) = delete;
    LinuxI2c(LinuxI2c&& other) noexcept;
    LinuxI2c& operator=(LinuxI2c&& other) noexcept;

    [[nodiscard]] bool write(std::span<const std::uint8_t> tx) noexcept;
    [[nodiscard]] bool read(std::span<std::uint8_t> rx) noexcept;

private:
    void close_fd() noexcept;

    int fd_{-1};
};

}  // namespace sht3x

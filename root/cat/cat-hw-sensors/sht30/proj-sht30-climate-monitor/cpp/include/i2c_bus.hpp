#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <utility>

#ifdef __linux__
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#endif

namespace sensors {

/**
 * @brief RAII-обгортка для безпечного управління доступом до шини I2C.
 * Забезпечує відкриття/закриття дескриптора пристрою, вибір веденого пристрою
 * та низькорівневі операції читання/запису.
 */
class I2CBus {
public:
    explicit I2CBus(const std::string& device_path = "/dev/i2c-1")
        : device_path_(device_path) {
#ifdef __linux__
        fd_ = ::open(device_path_.c_str(), O_RDWR);
#else
        // Симуляція відкритого дескриптора для тестового середовища
        fd_ = 1;
#endif
    }

    ~I2CBus() {
        close_bus();
    }

    // Забороняємо копіювання ресурсу
    I2CBus(const I2CBus&) = delete;
    I2CBus& operator=(const I2CBus&) = delete;

    // Дозволяємо переміщення ресурсу
    I2CBus(I2CBus&& other) noexcept 
        : fd_(other.fd_), slave_address_(other.slave_address_), device_path_(std::move(other.device_path_)) {
        other.fd_ = -1;
    }

    I2CBus& operator=(I2CBus&& other) noexcept {
        if (this != &other) {
            close_bus();
            fd_ = other.fd_;
            slave_address_ = other.slave_address_;
            device_path_ = std::move(other.device_path_);
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_open() const noexcept {
        return fd_ >= 0;
    }

    /**
     * @brief Встановлює I2C-адресу веденого пристрою (slave address).
     */
    bool set_slave_address(uint8_t address) {
        if (!is_open()) return false;
        slave_address_ = address;
#ifdef __linux__
        if (::ioctl(fd_, I2C_SLAVE, address) < 0) {
            return false;
        }
#endif
        return true;
    }

    /**
     * @brief Надсилає 16-бітну команду на пристрій (MSB перший).
     */
    bool write_command(uint16_t command) {
        if (!is_open()) return false;
        const uint8_t buf[2] = {
            static_cast<uint8_t>((command >> 8) & 0xFF),
            static_cast<uint8_t>(command & 0xFF)
        };
        return write_bytes(buf, 2);
    }

    /**
     * @brief Записує послідовність байтів у шину I2C.
     */
    bool write_bytes(const uint8_t* data, size_t length) {
        if (!is_open() || data == nullptr || length == 0) return false;
#ifdef __linux__
        const ssize_t res = ::write(fd_, data, length);
        return res == static_cast<ssize_t>(length);
#else
        (void)data;
        (void)length;
        return true;
#endif
    }

    /**
     * @brief Зчитує послідовність байтів із пристрою.
     */
    bool read_bytes(uint8_t* buffer, size_t length) {
        if (!is_open() || buffer == nullptr || length == 0) return false;
#ifdef __linux__
        const ssize_t res = ::read(fd_, buffer, length);
        return res == static_cast<ssize_t>(length);
#else
        // Емуляція зчитування кадрів SHT30 у разі відсутності Linux I2C
        // Повертає: T_raw = 0x6666 (25.0 °C, CRC = 0x93), RH_raw = 0x8000 (50.0 %, CRC = 0xA2)
        if (length == 6) {
            buffer[0] = 0x66; buffer[1] = 0x66; buffer[2] = 0x93;
            buffer[3] = 0x80; buffer[4] = 0x00; buffer[5] = 0xA2;
        }
        return true;
#endif
    }

private:
    void close_bus() noexcept {
        if (fd_ >= 0) {
#ifdef __linux__
            ::close(fd_);
#endif
            fd_ = -1;
        }
    }

    int fd_{-1};
    uint8_t slave_address_{0};
    std::string device_path_;
};

} // namespace sensors

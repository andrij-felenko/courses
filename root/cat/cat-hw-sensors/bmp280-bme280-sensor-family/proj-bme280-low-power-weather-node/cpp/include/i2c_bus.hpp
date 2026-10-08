#ifndef I2C_BUS_HPP
#define I2C_BUS_HPP

#include <string>
#include <cstdint>
#include <cstddef>
#include <vector>
#include <iostream>
#include <system_error>
#include <utility>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

#if defined(__linux__)
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#else
// Визначення константи I2C_SLAVE для сумісності та збірки на платформах без linux/i2c-dev.h
#ifndef I2C_SLAVE
#define I2C_SLAVE 0x0703
#endif
#endif

/**
 * @brief RAII-обгортка для управління апаратним ресурсом шини I2C в ОС Linux.
 * 
 * Клас відкриває файловий дескриптор пристрою I2C (наприклад, /dev/i2c-1)
 * у конструкторі та гарантовано закриває його у деструкторі.
 */
class I2CBus {
public:
    /**
     * @brief Конструктор відкриття I2C пристрою.
     * @param device_path Шлях до пристрою символьної шини (наприклад, "/dev/i2c-1").
     */
    explicit I2CBus(const std::string& device_path)
        : device_path_(device_path) {
        fd_ = ::open(device_path_.c_str(), O_RDWR);
        if (fd_ < 0) {
            std::cerr << "[I2CBus] Помилка відкриття шини: " << device_path_ << std::endl;
        }
    }

    /**
     * @brief Деструктор, що гарантовано звільняє апаратний ресурс.
     */
    ~I2CBus() {
        close_bus();
    }

    // Заборона копіювання для запобігання подвійному закриттю дескриптора
    I2CBus(const I2CBus&) = delete;
    I2CBus& operator=(const I2CBus&) = delete;

    // Дозвіл семантики переміщення (Move semantics)
    I2CBus(I2CBus&& other) noexcept
        : fd_(other.fd_), current_slave_addr_(other.current_slave_addr_), device_path_(std::move(other.device_path_)) {
        other.fd_ = -1;
        other.current_slave_addr_ = 0;
    }

    I2CBus& operator=(I2CBus&& other) noexcept {
        if (this != &other) {
            close_bus();
            fd_ = other.fd_;
            current_slave_addr_ = other.current_slave_addr_;
            device_path_ = std::move(other.device_path_);
            other.fd_ = -1;
            other.current_slave_addr_ = 0;
        }
        return *this;
    }

    /**
     * @brief Перевірка чи відкритий файловий дескриптор.
     */
    bool is_open() const noexcept {
        return fd_ >= 0;
    }

    /**
     * @brief Явне закриття дескриптора шини.
     */
    void close_bus() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
            current_slave_addr_ = 0;
        }
    }

    /**
     * @brief Налаштування адреси веденого пристрою (I2C Slave Address).
     * @param address 7-бітна I2C адреса пристрою.
     * @return true у разі успішного виклику ioctl.
     */
    bool set_slave_address(uint8_t address) {
        if (!is_open()) {
            return false;
        }
        if (current_slave_addr_ == address) {
            return true;
        }
        if (::ioctl(fd_, I2C_SLAVE, address) < 0) {
            std::cerr << "[I2CBus] Помилка встановлення I2C адреси 0x" 
                      << std::hex << static_cast<int>(address) << std::dec << std::endl;
            return false;
        }
        current_slave_addr_ = address;
        return true;
    }

    /**
     * @brief Запис 8-бітного значення у вказаний регістр.
     */
    bool write_register(uint8_t reg, uint8_t value) {
        if (!is_open()) {
            return false;
        }
        uint8_t buffer[2] = {reg, value};
        return ::write(fd_, buffer, 2) == 2;
    }

    /**
     * @brief Читання 8-бітного значення зі вказаного регістра.
     */
    bool read_register(uint8_t reg, uint8_t& value) {
        if (!is_open()) {
            return false;
        }
        if (::write(fd_, &reg, 1) != 1) {
            return false;
        }
        return ::read(fd_, &value, 1) == 1;
    }

    /**
     * @brief Поблокне зчитування послідовності байтів починаючи з reg.
     */
    bool read_bytes(uint8_t start_reg, uint8_t* buffer, size_t length) {
        if (!is_open() || buffer == nullptr || length == 0) {
            return false;
        }
        if (::write(fd_, &start_reg, 1) != 1) {
            return false;
        }
        return ::read(fd_, buffer, length) == static_cast<ssize_t>(length);
    }

    /**
     * @brief Поблокний запис послідовності байтів починаючи з reg.
     */
    bool write_bytes(uint8_t start_reg, const uint8_t* buffer, size_t length) {
        if (!is_open() || buffer == nullptr || length == 0) {
            return false;
        }
        std::vector<uint8_t> send_buf;
        send_buf.reserve(length + 1);
        send_buf.push_back(start_reg);
        send_buf.insert(send_buf.end(), buffer, buffer + length);
        return ::write(fd_, send_buf.data(), send_buf.size()) == static_cast<ssize_t>(send_buf.size());
    }

private:
    int fd_{-1};
    uint8_t current_slave_addr_{0};
    std::string device_path_;
};

#endif // I2C_BUS_HPP

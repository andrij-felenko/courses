#include "aht20_driver.hpp"
#include "aht20_crc.hpp"

#include <iostream>
#include <thread>
#include <chrono>
#include <cstring>

#ifdef __linux__
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#endif

namespace aht20 {

// ---------------------------------------------------------
// Реалізація I2cBusGuard (RAII-керування шиною I2C)
// ---------------------------------------------------------

I2cBusGuard::I2cBusGuard(const std::string& device_path, uint8_t address, bool mock_mode)
    : address_(address), mock_mode_(mock_mode), dev_path_(device_path) {
    if (mock_mode_) {
        fd_ = -1;
        return;
    }

#ifdef __linux__
    fd_ = ::open(dev_path_.c_str(), O_RDWR);
    if (fd_ >= 0) {
        if (::ioctl(fd_, I2C_SLAVE, address_) < 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }
#else
    // Автоматичний фолбек у mock-режим для не-Linux платформ
    mock_mode_ = true;
    fd_ = -1;
#endif
}

I2cBusGuard::~I2cBusGuard() {
    close_bus();
}

I2cBusGuard::I2cBusGuard(I2cBusGuard&& other) noexcept
    : fd_(other.fd_), address_(other.address_), mock_mode_(other.mock_mode_),
      dev_path_(std::move(other.dev_path_)), mock_status_(other.mock_status_),
      mock_measuring_(other.mock_measuring_) {
    other.fd_ = -1;
}

I2cBusGuard& I2cBusGuard::operator=(I2cBusGuard&& other) noexcept {
    if (this != &other) {
        close_bus();
        fd_ = other.fd_;
        address_ = other.address_;
        mock_mode_ = other.mock_mode_;
        dev_path_ = std::move(other.dev_path_);
        mock_status_ = other.mock_status_;
        mock_measuring_ = other.mock_measuring_;
        other.fd_ = -1;
    }
    return *this;
}

void I2cBusGuard::close_bus() noexcept {
#ifdef __linux__
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
#endif
}

bool I2cBusGuard::write_bytes(const uint8_t* data, size_t length) {
    if (mock_mode_) {
        if (length == 3 && data[0] == Aht20Driver::CMD_MEASURE[0]) {
            mock_measuring_ = true;
        } else if (length == 3 && data[0] == Aht20Driver::CMD_INIT[0]) {
            mock_status_ |= Aht20Driver::STATUS_CALIBRATED_MASK;
        } else if (length == 1 && data[0] == Aht20Driver::CMD_SOFT_RESET) {
            mock_status_ = Aht20Driver::STATUS_CALIBRATED_MASK;
            mock_measuring_ = false;
        }
        return true;
    }

#ifdef __linux__
    if (fd_ < 0) return false;
    ssize_t bytes_written = ::write(fd_, data, length);
    return bytes_written == static_cast<ssize_t>(length);
#else
    return false;
#endif
}

bool I2cBusGuard::read_bytes(uint8_t* buffer, size_t length) {
    if (mock_mode_) {
        if (length == 1) {
            // Зчитування байта статусу
            buffer[0] = mock_status_;
            return true;
        }
        if (length == 7) {
            // Симуляція 7-байтового кадру
            // Байт 0: Статус (calibrated, not busy)
            buffer[0] = mock_status_ & (~Aht20Driver::STATUS_BUSY_MASK);

            // Симуляція вологості: ~55.4% RH -> raw_humidity = 580935 (0x8DD47)
            uint32_t raw_h = 580935;
            // Симуляція температури: ~24.6 °C -> raw_temp = 391157 (0x5F7F5)
            uint32_t raw_t = 391157;

            buffer[1] = static_cast<uint8_t>((raw_h >> 12) & 0xFF);
            buffer[2] = static_cast<uint8_t>((raw_h >> 4) & 0xFF);
            buffer[3] = static_cast<uint8_t>(((raw_h & 0x0F) << 4) | ((raw_t >> 16) & 0x0F));
            buffer[4] = static_cast<uint8_t>((raw_t >> 8) & 0xFF);
            buffer[5] = static_cast<uint8_t>(raw_t & 0xFF);

            // Обчислення реальної CRC8 для симульованого кадру
            buffer[6] = Aht20Crc8::calculate(buffer, 6);

            mock_measuring_ = false;
            return true;
        }
        return false;
    }

#ifdef __linux__
    if (fd_ < 0) return false;
    ssize_t bytes_read = ::read(fd_, buffer, length);
    return bytes_read == static_cast<ssize_t>(length);
#else
    return false;
#endif
}

// ---------------------------------------------------------
// Реалізація Aht20Driver
// ---------------------------------------------------------

Aht20Driver::Aht20Driver(const std::string& i2c_path, uint8_t address, bool mock_mode)
    : bus_(i2c_path, address, mock_mode) {
    if (bus_.is_valid()) {
        initialize();
    }
}

Aht20Status Aht20Driver::read_status_byte(uint8_t& out_status) {
    if (!bus_.is_valid()) {
        return Aht20Status::ErrI2cTransfer;
    }
    if (!bus_.read_bytes(&out_status, 1)) {
        return Aht20Status::ErrI2cTransfer;
    }
    return Aht20Status::Success;
}

Aht20Status Aht20Driver::initialize() {
    uint8_t status = 0;
    Aht20Status st = read_status_byte(status);
    if (st != Aht20Status::Success) {
        return st;
    }

    // Перевіряємо прапор калібрування (Bit 3)
    if ((status & STATUS_CALIBRATED_MASK) == 0) {
        // Якщо давач не відкалібрований, надсилаємо команду ініціалізації 0xBE, 0x08, 0x00
        if (!bus_.write_bytes(CMD_INIT, 3)) {
            return Aht20Status::ErrI2cTransfer;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));

        // Повторна перевірка статусу
        st = read_status_byte(status);
        if (st != Aht20Status::Success) {
            return st;
        }
        if ((status & STATUS_CALIBRATED_MASK) == 0) {
            return Aht20Status::ErrNotCalibrated;
        }
    }

    is_initialized_ = true;
    return Aht20Status::Success;
}

Aht20Status Aht20Driver::trigger_measurement() {
    if (!is_initialized_) {
        Aht20Status st = initialize();
        if (st != Aht20Status::Success) {
            return st;
        }
    }

    if (!bus_.write_bytes(CMD_MEASURE, 3)) {
        return Aht20Status::ErrI2cTransfer;
    }
    return Aht20Status::Success;
}

Aht20Status Aht20Driver::read_measurement(Aht20Data& out_data, std::chrono::milliseconds timeout) {
    out_data.valid = false;

    // Моніторинг прапорця занятості (Bit 7 status byte)
    auto start = std::chrono::steady_clock::now();
    uint8_t status = 0;

    while (true) {
        Aht20Status st = read_status_byte(status);
        if (st != Aht20Status::Success) {
            return st;
        }

        if ((status & STATUS_BUSY_MASK) == 0) {
            break; // Давач завершив вимірювання
        }

        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start);
        if (elapsed >= timeout) {
            return Aht20Status::ErrTimeout;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // Зчитуємо 7-байтовий кадр (байти 0..5 - дані, 6 - CRC8)
    uint8_t frame[7] = {0};
    if (!bus_.read_bytes(frame, 7)) {
        return Aht20Status::ErrI2cTransfer;
    }

    // Верифікація циклічного надлишкового коду CRC8
    if (!Aht20Crc8::verify(frame, 7)) {
        return Aht20Status::ErrCrcMismatch;
    }

    // Розбір 20-бітних даних
    parse_raw_data(frame, out_data.temperature_c, out_data.humidity_rh);
    out_data.valid = true;

    return Aht20Status::Success;
}

Aht20Status Aht20Driver::read_sample(Aht20Data& out_data) {
    Aht20Status st = trigger_measurement();
    if (st != Aht20Status::Success) {
        return st;
    }

    // Рекомендована затримка для завершення вимірювання AHT20 (~80 мс)
    std::this_thread::sleep_for(std::chrono::milliseconds(80));

    return read_measurement(out_data);
}

Aht20Status Aht20Driver::soft_reset() {
    if (!bus_.write_bytes(&CMD_SOFT_RESET, 1)) {
        return Aht20Status::ErrI2cTransfer;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    is_initialized_ = false;
    return initialize();
}

void Aht20Driver::parse_raw_data(const uint8_t frame[7], float& out_temp, float& out_humidity) noexcept {
    // Відновлення 20-бітного значення вологості:
    // Byte 1 [19:12] + Byte 2 [11:4] + Byte 3 старші 4 біти [3:0]
    const uint32_t raw_humidity = (static_cast<uint32_t>(frame[1]) << 12) |
                                  (static_cast<uint32_t>(frame[2]) << 4) |
                                  (static_cast<uint32_t>(frame[3]) >> 4);

    // Відновлення 20-бітного значення температури:
    // Byte 3 молодші 4 біти [19:16] + Byte 4 [15:8] + Byte 5 [7:0]
    const uint32_t raw_temp = ((static_cast<uint32_t>(frame[3]) & 0x0F) << 16) |
                               (static_cast<uint32_t>(frame[4]) << 8) |
                                static_cast<uint32_t>(frame[5]);

    // Перетворення за формулами AHT20:
    // RH (%) = (S_rh / 2^20) * 100
    // T (°C) = (S_t / 2^20) * 200 - 50
    constexpr float TWO_POW_20 = 1048576.0f;

    out_humidity = (static_cast<float>(raw_humidity) / TWO_POW_20) * 100.0f;
    out_temp = (static_cast<float>(raw_temp) / TWO_POW_20) * 200.0f - 50.0f;
}

} // namespace aht20

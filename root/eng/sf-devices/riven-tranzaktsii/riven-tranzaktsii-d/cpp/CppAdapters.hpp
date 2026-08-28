/**
 * @file CppAdapters.hpp
 * @brief C++20 реалізація адаптерів I2C та SPI з RAII-керуванням лінією CS.
 */

#pragma once

#include "BusConcepts.hpp"
#include <functional>
#include <array>
#include <cstring>

namespace embedded::bus {

/**
 * @brief RAII-вартовий лінії Chip Select шини SPI.
 */
class CsGuard {
public:
    explicit CsGuard(std::function<void(bool)> cs_fn) : cs_fn_(std::move(cs_fn)) {
        if (cs_fn_) cs_fn_(true); // Активація (CS Low)
    }
    ~CsGuard() {
        if (cs_fn_) cs_fn_(false); // Деактивація (CS High)
    }

    CsGuard(const CsGuard&) = delete;
    CsGuard& operator=(const CsGuard&) = delete;

private:
    std::function<void(bool)> cs_fn_;
};

/**
 * @brief C++20 I2C Адаптер.
 */
class I2cAdapter final : public IBusAdapter {
public:
    I2cAdapter(uint8_t dev_addr, void* hal_handle)
        : dev_addr_(dev_addr), hal_handle_(hal_handle) {}

    std::expected<void, BusError> read_reg(uint16_t reg, std::span<uint8_t> rx) override {
        if (rx.empty()) return std::unexpected(BusError::InvalidParam);

        uint8_t reg_byte = static_cast<uint8_t>(reg & 0xFF);
        int res = hal_mock_i2c_write_read(dev_addr_, &reg_byte, 1, rx.data(), rx.size());
        if (res != 0) return std::unexpected(BusError::IoError);

        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg, std::span<const uint8_t> tx) override {
        if (tx.empty()) return std::unexpected(BusError::InvalidParam);

        std::array<uint8_t, 64> buffer{};
        if (tx.size() + 1 > buffer.size()) return std::unexpected(BusError::InvalidParam);

        buffer[0] = static_cast<uint8_t>(reg & 0xFF);
        std::memcpy(&buffer[1], tx.data(), tx.size());

        int res = hal_mock_i2c_write(dev_addr_, buffer.data(), tx.size() + 1);
        if (res != 0) return std::unexpected(BusError::IoError);

        return {};
    }

private:
    uint8_t dev_addr_;
    void*   hal_handle_;

    int hal_mock_i2c_write_read(uint8_t, const uint8_t*, size_t, uint8_t*, size_t) { return 0; }
    int hal_mock_i2c_write(uint8_t, const uint8_t*, size_t) { return 0; }
};

/**
 * @brief C++20 SPI Адаптер.
 */
class SpiAdapter final : public IBusAdapter {
public:
    SpiAdapter(std::function<void(bool)> cs_ctrl, void* hal_handle, bool read_msb = true)
        : cs_ctrl_(std::move(cs_ctrl)), hal_handle_(hal_handle), read_msb_(read_msb) {}

    std::expected<void, BusError> read_reg(uint16_t reg, std::span<uint8_t> rx) override {
        if (rx.empty()) return std::unexpected(BusError::InvalidParam);

        uint8_t addr_byte = static_cast<uint8_t>(reg & 0x7F);
        if (read_msb_) addr_byte |= 0x80;

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res != 0) return std::unexpected(BusError::IoError);

        res = hal_mock_spi_transfer(nullptr, rx.data(), rx.size());
        if (res != 0) return std::unexpected(BusError::IoError);

        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg, std::span<const uint8_t> tx) override {
        if (tx.empty()) return std::unexpected(BusError::InvalidParam);

        uint8_t addr_byte = static_cast<uint8_t>(reg & 0x7F);

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res == 0) {
            res = hal_mock_spi_transfer(tx.data(), nullptr, tx.size());
        }

        return (res == 0) ? std::expected<void, BusError>{} : std::unexpected(BusError::IoError);
    }

private:
    std::function<void(bool)> cs_ctrl_;
    void*                     hal_handle_;
    bool                      read_msb_;

    int hal_mock_spi_transfer(const uint8_t*, uint8_t*, size_t) { return 0; }
};

} // namespace embedded::bus

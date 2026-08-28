/**
 * @file CppAdapters.hpp
 * @brief C++20 реалізація адаптерів I2cAdapter, SpiAdapter та MockBusAdapter.
 */

#pragma once

#include "BusConcepts.hpp"
#include <array>
#include <vector>
#include <functional>
#include <cstring>

namespace embedded::bus {

/**
 * @brief RAII-обгортка керування лінією Chip Select шини SPI.
 */
class CsGuard {
public:
    explicit CsGuard(std::function<void(bool)> cs_fn) : cs_fn_(std::move(cs_fn)) {
        if (cs_fn_) cs_fn_(true); // Активний низький рівень (CS Low)
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
    I2cAdapter(uint8_t dev_addr, void* hal_handle, uint32_t timeout_ms = 100)
        : dev_addr_(dev_addr), hal_handle_(hal_handle), timeout_ms_(timeout_ms) {}

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (rx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t reg_byte = static_cast<uint8_t>(reg_addr & 0xFF);
        // Імітація виклику HAL write-read із Repeated START
        int res = hal_mock_i2c_transfer(dev_addr_, &reg_byte, 1, rx_data.data(), rx_data.size());
        if (res == 0) return {};
        if (res == -2) return std::unexpected(BusError::Nack);
        return std::unexpected(BusError::IoError);
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (tx_data.empty()) return std::unexpected(BusError::InvalidArg);

        std::array<uint8_t, 64> tx_buffer{};
        if (tx_data.size() + 1 > tx_buffer.size()) return std::unexpected(BusError::InvalidArg);

        tx_buffer[0] = static_cast<uint8_t>(reg_addr & 0xFF);
        std::memcpy(&tx_buffer[1], tx_data.data(), tx_data.size());

        int res = hal_mock_i2c_transmit(dev_addr_, tx_buffer.data(), tx_data.size() + 1);
        if (res == 0) return {};
        return std::unexpected(BusError::IoError);
    }

private:
    uint8_t  dev_addr_;
    void*    hal_handle_;
    uint32_t timeout_ms_;

    // Локальні заглушки для демонстрації
    int hal_mock_i2c_transfer(uint8_t, const uint8_t*, size_t, uint8_t*, size_t) { return 0; }
    int hal_mock_i2c_transmit(uint8_t, const uint8_t*, size_t) { return 0; }
};

/**
 * @brief C++20 SPI Адаптер із підтримкою RAII CS та прапорців автоінкременту.
 */
class SpiAdapter final : public IBusAdapter {
public:
    SpiAdapter(std::function<void(bool)> cs_ctrl, void* hal_handle, BusFlags flags = BusFlags::SpiReadMsb)
        : cs_ctrl_(std::move(cs_ctrl)), hal_handle_(hal_handle), flags_(flags) {}

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (rx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t addr_byte = static_cast<uint8_t>(reg_addr & 0x7F);
        if (has_flag(flags_, BusFlags::SpiReadMsb)) addr_byte |= 0x80;
        if (has_flag(flags_, BusFlags::AutoInc))    addr_byte |= 0x40;

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res != 0) return std::unexpected(BusError::IoError);

        res = hal_mock_spi_transfer(nullptr, rx_data.data(), rx_data.size());
        if (res != 0) return std::unexpected(BusError::IoError);

        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (tx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t addr_byte = static_cast<uint8_t>(reg_addr & 0x7F);
        if (has_flag(flags_, BusFlags::AutoInc)) addr_byte |= 0x40;

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res == 0) {
            res = hal_mock_spi_transfer(tx_data.data(), nullptr, tx_data.size());
        }

        return (res == 0) ? std::expected<void, BusError>{} : std::unexpected(BusError::IoError);
    }

private:
    std::function<void(bool)> cs_ctrl_;
    void*                     hal_handle_;
    BusFlags                  flags_;

    int hal_mock_spi_transfer(const uint8_t*, uint8_t*, size_t) { return 0; }
};

/**
 * @brief C++20 Mock Адаптер для автоматизованого тестування (Host Unit Testing).
 */
class MockBusAdapter final : public IBusAdapter {
public:
    MockBusAdapter() {
        memory_.fill(0x00);
    }

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (inject_nack_) return std::unexpected(BusError::Nack);
        if (reg_addr + rx_data.size() > memory_.size()) return std::unexpected(BusError::InvalidArg);

        std::memcpy(rx_data.data(), &memory_[reg_addr], rx_data.size());
        read_count_++;
        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (inject_nack_) return std::unexpected(BusError::Nack);
        if (reg_addr + tx_data.size() > memory_.size()) return std::unexpected(BusError::InvalidArg);

        std::memcpy(&memory_[reg_addr], tx_data.data(), tx_data.size());
        write_count_++;
        return {};
    }

    void set_reg(uint8_t reg, uint8_t val) noexcept { memory_[reg] = val; }
    [[nodiscard]] uint8_t get_reg(uint8_t reg) const noexcept { return memory_[reg]; }
    void set_inject_nack(bool enable) noexcept { inject_nack_ = enable; }
    [[nodiscard]] size_t read_count() const noexcept { return read_count_; }
    [[nodiscard]] size_t write_count() const noexcept { return write_count_; }

private:
    std::array<uint8_t, 256> memory_{};
    bool                     inject_nack_{false};
    size_t                   read_count_{0};
    size_t                   write_count_{0};
};

} // namespace embedded::bus

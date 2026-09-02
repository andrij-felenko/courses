#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "peripherals.hpp"

namespace drv {

enum class I2cError : std::uint8_t {
    Timeout,   // ведений розтягує такт довше за будь-який розумний ліміт
    Nack,      // AF: на 9-му такті ніхто не притягнув SDA
    ArbitrationLost,  // ARLO: на шині виявився інший ведучий
    BusError,  // BERR: START/STOP посеред байта
    BusBusy,   // шина не звільнилася — привід кликати відновлення
    BadLength
};

class I2cMaster {
public:
    I2cMaster(mcu::I2cRegs& regs, std::uint32_t pclk1Hz, std::uint32_t sclHz) noexcept;

    [[nodiscard]] std::expected<void, I2cError> write(std::uint8_t address7,
                                                     std::span<const std::uint8_t> data) noexcept;
    [[nodiscard]] std::expected<void, I2cError> read(std::uint8_t address7,
                                                    std::span<std::uint8_t> data) noexcept;
    // Читання регістра давача: команда, повторний START, відповідь
    [[nodiscard]] std::expected<void, I2cError> writeRead(std::uint8_t address7,
                                                         std::span<const std::uint8_t> command,
                                                         std::span<std::uint8_t> data) noexcept;

private:
    // Поки об'єкт живий, транзакція вважається незавершеною: деструктор сам
    // видасть STOP на будь-якому ранньому виході, щоб шина не лишилася зайнятою.
    class StopGuard {
    public:
        explicit StopGuard(mcu::I2cRegs& regs) noexcept : regs_{&regs} {}
        ~StopGuard()
        {
            if (regs_ != nullptr) {
                regs_->cr1 |= mcu::i2c_cr1::stop;
            }
        }
        void dismiss() noexcept { regs_ = nullptr; }
        StopGuard(const StopGuard&) = delete;
        StopGuard& operator=(const StopGuard&) = delete;

    private:
        mcu::I2cRegs* regs_;
    };

    [[nodiscard]] std::expected<void, I2cError> waitFlag(std::uint32_t sr1Mask) noexcept;
    [[nodiscard]] std::expected<void, I2cError> waitStopDone() noexcept;
    [[nodiscard]] std::expected<void, I2cError> sendStart(bool repeated) noexcept;
    [[nodiscard]] std::expected<void, I2cError> sendAddress(std::uint8_t address7, bool read) noexcept;
    void clearAddressFlag() noexcept;
    [[nodiscard]] std::expected<void, I2cError> writeBody(std::span<const std::uint8_t> data) noexcept;
    [[nodiscard]] std::expected<void, I2cError> readBody(std::span<std::uint8_t> data) noexcept;

    mcu::I2cRegs& regs_;
    static constexpr std::uint32_t pollBudget = 200000u;
};

}  // namespace drv

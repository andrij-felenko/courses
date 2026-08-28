#include <cstdint>
#include <expected>
#include <array>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"
#include "i2c_bus_recovery.hpp"
#include "reset_escalation_controller.hpp"
#include "sensor_state_recovery.hpp"
#include "bus_diagnostics.hpp"

class ResilientBmp280Driver {
public:
    enum class DriverError : uint8_t {
        BusError,
        InvalidChipId,
        FatalPeripheralLockup
    };

    struct RawMeasurement {
        int32_t raw_temperature{0};
        uint32_t raw_pressure{0};
    };

    ResilientBmp280Driver(EscalationManager::Config cfg, uint8_t i2c_addr = 0x76) noexcept
        : escalation_{cfg}, i2c_hw_{cfg.i2c, cfg.scl_pin, cfg.sda_pin}, i2c_addr_{i2c_addr} {
        DwtTimer::global_init();
        shadow_.set_register(0xF4 /* CTRL_MEAS */, 0x57);
        shadow_.set_register(0xF5 /* CONFIG */, 0x10);
    }

    [[nodiscard]] std::expected<void, DriverError> initialize() noexcept {
        auto check_id = [this]() -> bool {
            auto val = raw_read_byte(0xD0);
            return val.has_value() && *val == 0x58;
        };

        if (!check_id()) {
            return recover_escalation();
        }

        // Запис конфігурації
        for (const auto& reg : shadow_.registers()) {
            if (!raw_write_byte(reg.address, reg.value)) {
                return recover_escalation();
            }
        }

        escalation_.record_success();
        diag_log_.record(DiagnosticEventType::RecoverySuccess, 1, 0);
        return {};
    }

    [[nodiscard]] std::expected<RawMeasurement, DriverError> read_sample() noexcept {
        std::array<uint8_t, 6> raw_buf{};
        for (size_t i = 0; i < 6; ++i) {
            auto b = raw_read_byte(static_cast<uint8_t>(0xF7 + i));
            if (!b) {
                auto rec_res = recover_escalation();
                if (!rec_res) return std::unexpected(rec_res.error());
                return std::unexpected(DriverError::BusError);
            }
            raw_buf[i] = *b;
        }

        RawMeasurement m{};
        m.raw_pressure = (static_cast<uint32_t>(raw_buf[0]) << 12) |
                         (static_cast<uint32_t>(raw_buf[1]) << 4) |
                         (static_cast<uint32_t>(raw_buf[2]) >> 4);
        m.raw_temperature = (static_cast<int32_t>(raw_buf[3]) << 12) |
                            (static_cast<int32_t>(raw_buf[4]) << 4) |
                            (static_cast<int32_t>(raw_buf[5]) >> 4);
        return m;
    }

private:
    EscalationManager escalation_;
    I2cBusRecoveryEngine::Hardware i2c_hw_;
    SensorShadowCache<8, 32> shadow_{};
    DiagnosticLog<32> diag_log_{};
    uint8_t i2c_addr_{0x76};

    [[nodiscard]] std::expected<void, DriverError> recover_escalation() noexcept {
        const auto tier = escalation_.escalate_fault();
        diag_log_.record(static_cast<DiagnosticEventType>(static_cast<uint8_t>(DiagnosticEventType::Tier1SoftReset) + static_cast<uint8_t>(tier) - 1), 1, -1);

        if (tier == EscalationTier::Fatal) {
            return std::unexpected(DriverError::FatalPeripheralLockup);
        }

        // Перевірка готовності чипа після скидання
        auto id = raw_read_byte(0xD0);
        if (!id || *id != 0x58) {
            return std::unexpected(DriverError::InvalidChipId);
        }

        // Відновлення конфігурації
        for (const auto& reg : shadow_.registers()) {
            if (!raw_write_byte(reg.address, reg.value)) {
                return std::unexpected(DriverError::BusError);
            }
        }

        escalation_.record_success();
        diag_log_.record(DiagnosticEventType::RecoverySuccess, 1, 0);
        return {};
    }

    [[nodiscard]] std::expected<uint8_t, DriverError> raw_read_byte(uint8_t reg) const noexcept {
        auto* i2c = i2c_hw_.i2c;
        const DwtTimer timer{std::chrono::microseconds{2000}};

        // Wait busy
        if (!timer.wait_until([i2c] { return (i2c->SR2 & I2C_SR2_BUSY) == 0; })) return std::unexpected(DriverError::BusError);

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>(i2c_addr_ << 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        (void)i2c->SR2;

        i2c->DR = reg;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_TXE) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>((i2c_addr_ << 1) | 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        i2c->CR1 &= ~I2C_CR1_ACK;
        (void)i2c->SR2;
        i2c->CR1 |= I2C_CR1_STOP;

        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_RXNE) != 0; })) return std::unexpected(DriverError::BusError);
        return static_cast<uint8_t>(i2c->DR);
    }

    [[nodiscard]] std::expected<void, DriverError> raw_write_byte(uint8_t reg, uint8_t val) const noexcept {
        auto* i2c = i2c_hw_.i2c;
        const DwtTimer timer{std::chrono::microseconds{2000}};

        if (!timer.wait_until([i2c] { return (i2c->SR2 & I2C_SR2_BUSY) == 0; })) return std::unexpected(DriverError::BusError);

        i2c->CR1 |= I2C_CR1_START;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_SB) != 0; })) return std::unexpected(DriverError::BusError);

        i2c->DR = static_cast<uint8_t>(i2c_addr_ << 1);
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_ADDR) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }
        (void)i2c->SR2;

        i2c->DR = reg;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_TXE) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->DR = val;
        if (!timer.wait_until([i2c] { return (i2c->SR1 & I2C_SR1_BTF) != 0; })) {
            i2c->CR1 |= I2C_CR1_STOP;
            return std::unexpected(DriverError::BusError);
        }

        i2c->CR1 |= I2C_CR1_STOP;
        return {};
    }
};

#include "portable_hal_cxx20.h"
#include <array>
#include <algorithm>

namespace hal::mock {

class MockGpioPin {
public:
    Status init(const PinConfig& cfg) noexcept {
        mode_ = cfg.mode;
        level_ = PinLevel::Low;
        toggle_count_ = 0;
        return Status::Ok;
    }

    Status set_level(PinLevel lvl) noexcept {
        level_ = lvl;
        return Status::Ok;
    }

    [[nodiscard]] PinLevel get_level() const noexcept {
        return level_;
    }

    Status toggle() noexcept {
        level_ = (level_ == PinLevel::Low) ? PinLevel::High : PinLevel::Low;
        ++toggle_count_;
        return Status::Ok;
    }

    [[nodiscard]] uint32_t toggle_count() const noexcept { return toggle_count_; }

private:
    PinMode mode_{PinMode::OutputPushPull};
    PinLevel level_{PinLevel::Low};
    uint32_t toggle_count_{0};
};
static_assert(GpioPin<MockGpioPin>, "MockGpioPin must satisfy GpioPin concept");

template <size_t MemSize = 256>
class MockI2cBus {
public:
    explicit MockI2cBus(uint8_t target_addr) noexcept : expected_addr_(target_addr) {
        registers_.fill(0x00);
    }

    Status write(uint8_t addr, std::span<const uint8_t> tx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;
        if (tx.empty()) return Status::InvalidArg;

        uint8_t reg = tx[0];
        for (size_t i = 1; i < tx.size(); ++i) {
            if (reg + i - 1 < MemSize) {
                registers_[reg + i - 1] = tx[i];
            }
        }
        return Status::Ok;
    }

    Status read(uint8_t addr, std::span<uint8_t> rx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;

        for (size_t i = 0; i < rx.size(); ++i) {
            rx[i] = (i < MemSize) ? registers_[i] : 0xFF;
        }
        return Status::Ok;
    }

    Status write_read(uint8_t addr, std::span<const uint8_t> tx,
                       std::span<uint8_t> rx, uint32_t) noexcept {
        if (force_nack_ || addr != expected_addr_) return Status::Nack;
        if (tx.empty()) return Status::InvalidArg;

        uint8_t start_reg = tx[0];
        for (size_t i = 0; i < rx.size(); ++i) {
            size_t idx = start_reg + i;
            rx[i] = (idx < MemSize) ? registers_[idx] : 0x00;
        }
        return Status::Ok;
    }

    void set_reg(uint8_t reg, uint8_t val) noexcept { registers_[reg] = val; }
    [[nodiscard]] uint8_t get_reg(uint8_t reg) const noexcept { return registers_[reg]; }
    void set_force_nack(bool nack) noexcept { force_nack_ = nack; }

private:
    std::array<uint8_t, MemSize> registers_{};
    uint8_t expected_addr_{0x00};
    bool force_nack_{false};
};
static_assert(I2cMaster<MockI2cBus<256>>, "MockI2cBus must satisfy I2cMaster concept");

template <size_t MemSize = 1024>
class MockSpiBus {
public:
    Status transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx, uint32_t) noexcept {
        size_t len = std::max(tx.size(), rx.size());
        for (size_t i = 0; i < len; ++i) {
            uint8_t b = (i < tx.size()) ? tx[i] : 0xFF;
            if (i < rx.size()) rx[i] = b;
        }
        return Status::Ok;
    }

    Status write(std::span<const uint8_t> tx, uint32_t timeout) noexcept {
        return transfer(tx, {}, timeout);
    }

    Status read(std::span<uint8_t> rx, uint32_t timeout) noexcept {
        return transfer({}, rx, timeout);
    }
};
static_assert(SpiMaster<MockSpiBus<1024>>, "MockSpiBus must satisfy SpiMaster concept");

} // namespace hal::mock

namespace hal::stm32 {

struct GpioRegisters {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
};

template <uintptr_t PortBase, uint8_t PinIndex>
requires (PinIndex <= 15)
class StaticGpioPin {
public:
    static inline GpioRegisters* const Port = reinterpret_cast<GpioRegisters*>(PortBase);

    static Status init(const PinConfig& cfg) noexcept {
        Port->MODER &= ~(3U << (PinIndex * 2));
        if (cfg.mode == PinMode::OutputPushPull || cfg.mode == PinMode::OutputOpenDrain) {
            Port->MODER |= (1U << (PinIndex * 2));
        }

        if (cfg.mode == PinMode::OutputOpenDrain) {
            Port->OTYPER |= (1U << PinIndex);
        } else {
            Port->OTYPER &= ~(1U << PinIndex);
        }

        Port->PUPDR &= ~(3U << (PinIndex * 2));
        if (cfg.pull == PinPull::Up) {
            Port->PUPDR |= (1U << (PinIndex * 2));
        } else if (cfg.pull == PinPull::Down) {
            Port->PUPDR |= (2U << (PinIndex * 2));
        }
        return Status::Ok;
    }

    static Status set_level(PinLevel lvl) noexcept {
        if (lvl == PinLevel::High) {
            Port->BSRR = (1U << PinIndex);
        } else {
            Port->BSRR = (1U << (PinIndex + 16));
        }
        return Status::Ok;
    }

    [[nodiscard]] static PinLevel get_level() noexcept {
        return (Port->IDR & (1U << PinIndex)) ? PinLevel::High : PinLevel::Low;
    }

    static Status toggle() noexcept {
        Port->ODR ^= (1U << PinIndex);
        return Status::Ok;
    }
};

} // namespace hal::stm32

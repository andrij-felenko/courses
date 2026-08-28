#ifndef RESET_ESCALATION_CONTROLLER_HPP
#define RESET_ESCALATION_CONTROLLER_HPP

#include <cstdint>
#include <chrono>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"
#include "i2c_bus_recovery.hpp"

enum class EscalationTier : uint8_t {
    None,
    Tier1SoftReset,
    Tier2PinReset,
    Tier3PowerCycle,
    Fatal
};

struct PowerSwitchPin {
    GPIO_TypeDef* port{nullptr};
    uint8_t pin{0};
    bool active_high{false}; // false для P-MOSFET

    void configure() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (1U << (pin * 2));
        turn_on();
    }

    void turn_on() const noexcept {
        if (active_high) port->BSRR = (1U << pin);
        else port->BSRR = (1U << (pin + 16));
    }

    void turn_off() const noexcept {
        if (active_high) port->BSRR = (1U << (pin + 16));
        else port->BSRR = (1U << pin);
    }
};

class EscalationManager {
public:
    struct Config {
        PowerSwitchPin power_switch{};
        GpioPinConfig nrst_pin{};
        GpioPinConfig scl_pin{};
        GpioPinConfig sda_pin{};
        I2C_TypeDef* i2c{nullptr};
        std::chrono::milliseconds reset_pulse{5};
        std::chrono::milliseconds reset_settle{20};
        std::chrono::milliseconds power_off_duration{50};
        std::chrono::milliseconds power_on_settle{20};
    };

    explicit EscalationManager(Config cfg) noexcept : cfg_{cfg} {
        if (cfg_.power_switch.port) {
            cfg_.power_switch.configure();
        }
        if (cfg_.nrst_pin.port) {
            cfg_.nrst_pin.port->MODER &= ~(3U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.port->MODER |= (1U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.set_high();
        }
    }

    EscalationTier escalate_fault() noexcept {
        ++consecutive_failures_;

        if (consecutive_failures_ == 1) {
            current_tier_ = EscalationTier::Tier1SoftReset;
            I2cBusRecoveryEngine::execute({cfg_.i2c, cfg_.scl_pin, cfg_.sda_pin});
            ++total_tier1_;
        } else if (consecutive_failures_ == 2) {
            current_tier_ = EscalationTier::Tier2PinReset;
            execute_tier2_pin_reset();
            ++total_tier2_;
        } else if (consecutive_failures_ == 3) {
            current_tier_ = EscalationTier::Tier3PowerCycle;
            execute_tier3_power_cycle();
            ++total_tier3_;
        } else {
            current_tier_ = EscalationTier::Fatal;
        }

        return current_tier_;
    }

    void record_success() noexcept {
        consecutive_failures_ = 0;
        current_tier_ = EscalationTier::None;
    }

    [[nodiscard]] EscalationTier current_tier() const noexcept { return current_tier_; }

private:
    Config cfg_;
    EscalationTier current_tier_{EscalationTier::None};
    uint8_t consecutive_failures_{0};
    uint32_t total_tier1_{0};
    uint32_t total_tier2_{0};
    uint32_t total_tier3_{0};

    void execute_tier2_pin_reset() const noexcept {
        if (!cfg_.nrst_pin.port) return;
        cfg_.nrst_pin.set_low();
        DwtTimer::delay(cfg_.reset_pulse);
        cfg_.nrst_pin.set_high();
        DwtTimer::delay(cfg_.reset_settle);
    }

    void execute_tier3_power_cycle() const noexcept {
        if (!cfg_.power_switch.port) return;

        // 1. Hi-Z ізоляція
        isolate_pin(cfg_.scl_pin);
        isolate_pin(cfg_.sda_pin);
        if (cfg_.nrst_pin.port) isolate_pin(cfg_.nrst_pin);

        // 2. Знеструмлення
        cfg_.power_switch.turn_off();
        DwtTimer::delay(cfg_.power_off_duration);

        // 3. Увімкнення живлення
        cfg_.power_switch.turn_on();
        DwtTimer::delay(cfg_.power_on_settle);

        // 4. Відновлення nRESET
        if (cfg_.nrst_pin.port) {
            cfg_.nrst_pin.port->MODER &= ~(3U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.port->MODER |= (1U << (cfg_.nrst_pin.pin * 2));
            cfg_.nrst_pin.set_high();
        }

        // 5. Відновлення шини
        cfg_.scl_pin.set_alternate_function_open_drain();
        cfg_.sda_pin.set_alternate_function_open_drain();
    }

    static void isolate_pin(const GpioPinConfig& pin) noexcept {
        pin.port->MODER |= (3U << (pin.pin * 2));   // Analog
        pin.port->PUPDR &= ~(3U << (pin.pin * 2));  // No Pull
    }
};

#endif // RESET_ESCALATION_CONTROLLER_HPP

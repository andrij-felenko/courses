// early_pin_guard.cpp
#include "early_pin_guard.hpp"

namespace SystemSafety {

struct HardwareGpioPort {
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

[[nodiscard]] static inline bool lock_hardware_pin(HardwareGpioPort* port, uint8_t pin) noexcept {
    const uint32_t pin_mask = (1UL << pin);
    const uint32_t key_mask = pin_mask | (1UL << 16);

    port->LCKR = key_mask;
    port->LCKR = pin_mask;
    port->LCKR = key_mask;
    [[maybe_unused]] volatile uint32_t r1 = port->LCKR;
    return (port->LCKR & (1UL << 16)) != 0;
}

bool PinIntegrityGuard::verify_port_bridging(uintptr_t port_base, uint16_t pin_mask) noexcept {
    auto* port = reinterpret_cast<HardwareGpioPort*>(port_base);

    for (uint8_t pin = 0; pin < 16; ++pin) {
        if ((pin_mask & (1U << pin)) != 0) {
            const uint32_t shift2 = pin * 2;
            port->MODER &= ~(0b11UL << shift2);
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b01UL << shift2);
        }
    }

    for (volatile int d = 0; d < 300; ++d) { asm volatile ("nop"); }

    for (uint8_t pin = 0; pin < 16; ++pin) {
        if ((pin_mask & (1U << pin)) != 0) {
            const uint32_t shift2 = pin * 2;

            port->BSRR = (1UL << (pin + 16));
            port->MODER = (port->MODER & ~(0b11UL << shift2)) | (0b01UL << shift2);

            for (volatile int d = 0; d < 100; ++d) { asm volatile ("nop"); }

            const uint32_t idr_val = port->IDR & pin_mask;
            const uint32_t expected_val = pin_mask & ~(1UL << pin);

            if (idr_val != expected_val) {
                return false;
            }

            port->MODER &= ~(0b11UL << shift2);
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b01UL << shift2);
            for (volatile int d = 0; d < 100; ++d) { asm volatile ("nop"); }
        }
    }

    return true;
}

template <std::size_t N>
constexpr auto PinIntegrityGuard::verify_and_arm(const std::array<PinConfig, N>& configs) noexcept
    -> std::expected<DiagnosticReport, DiagnosticReport>
{
    asm volatile ("dsb 0xF" ::: "memory");

    for (std::size_t idx = 0; idx < N; ++idx) {
        const auto& cfg = configs[idx];
        auto* port = reinterpret_cast<HardwareGpioPort*>(cfg.port_base);
        const uint32_t shift2 = cfg.pin_index * 2;

        // Діагностика лінії
        if (cfg.expected_hardware == HardwareLineExpectation::HardPullDown) {
            // Вхід + Pull-Up
            port->MODER &= ~(0b11UL << shift2);
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b01UL << shift2);

            for (volatile int d = 0; d < 300; ++d) { asm volatile ("nop"); }

            if ((port->IDR & (1UL << cfg.pin_index)) != 0) {
                return std::unexpected(DiagnosticReport{
                    .verified_count = idx,
                    .faulty_index = idx,
                    .status = GuardStatus::MissingPullDown
                });
            }

            // Перевірка на КЗ до VDD
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b10UL << shift2);
            for (volatile int d = 0; d < 300; ++d) { asm volatile ("nop"); }

            if ((port->IDR & (1UL << cfg.pin_index)) != 0) {
                return std::unexpected(DiagnosticReport{
                    .verified_count = idx,
                    .faulty_index = idx,
                    .status = GuardStatus::ShortToVdd
                });
            }
        }
        else if (cfg.expected_hardware == HardwareLineExpectation::HardPullUp) {
            port->MODER &= ~(0b11UL << shift2);
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b10UL << shift2);

            for (volatile int d = 0; d < 300; ++d) { asm volatile ("nop"); }

            if ((port->IDR & (1UL << cfg.pin_index)) == 0) {
                return std::unexpected(DiagnosticReport{
                    .verified_count = idx,
                    .faulty_index = idx,
                    .status = GuardStatus::MissingPullUp
                });
            }
        }

        // Попереднє зведення рівня
        if (cfg.target_state == TargetState::OutputInactiveLow) {
            port->BSRR = (1UL << (cfg.pin_index + 16));
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b10UL << shift2);
            port->OSPEEDR &= ~(0b11UL << shift2);
            port->MODER = (port->MODER & ~(0b11UL << shift2)) | (0b01UL << shift2);
        } else if (cfg.target_state == TargetState::OutputActiveHigh) {
            port->BSRR = (1UL << cfg.pin_index);
            port->PUPDR = (port->PUPDR & ~(0b11UL << shift2)) | (0b01UL << shift2);
            port->OSPEEDR &= ~(0b11UL << shift2);
            port->MODER = (port->MODER & ~(0b11UL << shift2)) | (0b01UL << shift2);
        } else {
            port->MODER &= ~(0b11UL << shift2);
        }

        // Блокування
        if (cfg.lock_configuration) {
            if (!lock_hardware_pin(port, cfg.pin_index)) {
                return std::unexpected(DiagnosticReport{
                    .verified_count = idx,
                    .faulty_index = idx,
                    .status = GuardStatus::LockFailed
                });
            }
        }
    }

    return DiagnosticReport{
        .verified_count = N,
        .faulty_index = 0,
        .status = GuardStatus::Ok
    };
}

void PinIntegrityGuard::execute_emergency_shutdown(const DiagnosticReport& /*report*/) noexcept {
    asm volatile ("cpsid i" ::: "memory");
    while (true) {
        asm volatile ("wfi");
    }
}

} // namespace SystemSafety

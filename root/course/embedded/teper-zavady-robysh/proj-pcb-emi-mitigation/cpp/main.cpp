#include <cstdint>
#include <span>
#include <array>

namespace emi {

enum class SlewRate : uint32_t {
    Low2MHz     = 0x00U, // Фронти ~15-25 нс: UART, LED, низькочастотні сигнали
    Medium25MHz = 0x01U, // Фронти ~4-6 нс: SPI до 10 МГц, стандартні шини
    Fast50MHz   = 0x02U, // Фронти ~2-3 нс: швидкий SPI, інтерфейси датчиків
    High100MHz  = 0x03U  // Фронти <1.2 нс: лише QSPI/SDIO/FMC
};

// Абстракція регістра порту GPIO на базі адреси
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

struct PinSlewConfig {
    GpioRegisters *port;
    uint16_t       pin_mask;
    SlewRate       slew_rate;
};

class EmiController {
public:
    static constexpr void applySlewRates(std::span<const PinSlewConfig> configs) noexcept
    {
        for (const auto& cfg : configs) {
            if (cfg.port == nullptr) {
                continue;
            }

            const auto speed_val = static_cast<uint32_t>(cfg.slew_rate);
            for (uint32_t pin = 0; pin < 16; ++pin) {
                if (cfg.pin_mask & (1U << pin)) {
                    const uint32_t shift = pin * 2U;
                    const uint32_t mask = 0x03U << shift;
                    
                    uint32_t reg_val = cfg.port->OSPEEDR;
                    reg_val = (reg_val & ~mask) | (speed_val << shift);
                    cfg.port->OSPEEDR = reg_val;
                }
            }
        }
    }
};

} // namespace emi

// Адреси портів для конкретного мікроконтролера
inline auto* const PORTA = reinterpret_cast<emi::GpioRegisters*>(0x40020000UL);
inline auto* const PORTB = reinterpret_cast<emi::GpioRegisters*>(0x40020400UL);
inline auto* const PORTC = reinterpret_cast<emi::GpioRegisters*>(0x40020800UL);

void configure_board_emi_profiles()
{
    static constexpr std::array<emi::PinSlewConfig, 4> pin_profiles{{
        { PORTC, (1U << 13) | (1U << 14), emi::SlewRate::Low2MHz },     // LED / Силові ключі
        { PORTA, (1U << 9)  | (1U << 10), emi::SlewRate::Low2MHz },     // UART зв'язку
        { PORTB, (1U << 6)  | (1U << 7),  emi::SlewRate::Medium25MHz }, // I2C датчиків
        { PORTA, (1U << 5),               emi::SlewRate::Fast50MHz }    // SPI тактовий сигнал
    }};

    emi::EmiController::applySlewRates(pin_profiles);
}

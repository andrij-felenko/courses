#include "stm32f4xx.h"
#include <cstdint>
#include <span>

namespace mcu::gpio {

enum class Mode : uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class Speed : uint32_t {
    Low      = 0b00, // 2–4 MHz, мінімум завад EMI
    Medium   = 0b01, // 10–25 MHz
    High     = 0b10, // 50 MHz
    VeryHigh = 0b11  // 100+ MHz (тільки для швидкісних шин)
};

enum class Pull : uint32_t {
    None = 0b00,
    Up   = 0b01,
    Down = 0b10
};

/**
 * @brief Безпечний типізований конфігуратор виводів GPIO (RAII / Zero-cost abstraction).
 */
class PinGuard {
public:
    constexpr PinGuard(GPIO_TypeDef* port, uint8_t pin) noexcept
        : port_{port}, pin_{pin} {}

    void configure(Mode mode, Speed speed, Pull pull, uint8_t alternate_func = 0) const noexcept {
        // Захист системних виводів налагодження SWD (PA13 / PA14)
        if (port_ == GPIOA && (pin_ == 13 || pin_ == 14)) {
            // Відхиляємо переналаштування SWD під звичайний вихід
            if (mode == Mode::Output) {
                return;
            }
        }

        const uint32_t pin_2bit = pin_ * 2U;
        
        // Налаштування режиму роботи (MODER)
        port_->MODER = (port_->MODER & ~(0x3U << pin_2bit)) | 
                       (static_cast<uint32_t>(mode) << pin_2bit);

        // Налаштування швидкості наростання фронту (OSPEEDR)
        port_->OSPEEDR = (port_->OSPEEDR & ~(0x3U << pin_2bit)) | 
                         (static_cast<uint32_t>(speed) << pin_2bit);

        // Налаштування підтяжок (PUPDR)
        port_->PUPDR = (port_->PUPDR & ~(0x3U << pin_2bit)) | 
                       (static_cast<uint32_t>(pull) << pin_2bit);

        // Налаштування мультиплексора альтернативних функцій (AFR)
        if (mode == Mode::Alternate) {
            const uint32_t afr_idx = pin_ / 8U;
            const uint32_t afr_shift = (pin_ % 8U) * 4U;
            port_->AFR[afr_idx] = (port_->AFR[afr_idx] & ~(0xFU << afr_shift)) | 
                                  ((alternate_func & 0xFU) << afr_shift);
        }
    }

private:
    GPIO_TypeDef* port_;
    uint8_t pin_;
};

} // namespace mcu::gpio

void pinout_safe_init_cpp() {
    // Увімкнення тактування шини GPIO
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;

    // Конфігурація швидкісної лінії тактування SPI1_SCK на PA5 (AF5)
    constexpr mcu::gpio::PinGuard spi_sck{GPIOA, 5};
    spi_sck.configure(mcu::gpio::Mode::Alternate, 
                      mcu::gpio::Speed::High, 
                      mcu::gpio::Pull::None, 
                      5U); // AF5 = SPI1

    // Конфігурація статусного світлодіода на PB6
    constexpr mcu::gpio::PinGuard led_status{GPIOB, 6};
    led_status.configure(mcu::gpio::Mode::Output, 
                         mcu::gpio::Speed::Low, 
                         mcu::gpio::Pull::None);
}

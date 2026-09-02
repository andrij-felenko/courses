#pragma once

#include "stm32f10x.h"

#include <cstdint>

namespace hw {

/* Вивід із відкритим стоком. Підняти лінію транзистор не вміє: він або тягне її
   до землі, або відпускає — рівень 1 робить зовнішній резистор підтяжки. Звідси
   й імена методів: pull_low() і release(), а не set(true)/set(false). */
class OpenDrainPin {
public:
    enum class Mode : std::uint32_t {
        Gpio = 0x7U,               /* вихід Open-Drain 10 МГц, веде процесор */
        AlternateFunction = 0xBU,  /* той самий вихід, але веде периферія */
    };

    constexpr OpenDrainPin(GPIO_TypeDef* port, unsigned pin) noexcept
        : port_{port}, pin_{pin} {}

    void set_mode(Mode mode) const noexcept {
        /* Виводи 0..7 описує CRL, 8..15 — CRH; по чотири біти CNF+MODE на вивід */
        volatile std::uint32_t& cr = (pin_ < 8U) ? port_->CRL : port_->CRH;
        const unsigned shift = (pin_ % 8U) * 4U;
        cr = (cr & ~(0xFU << shift)) | (static_cast<std::uint32_t>(mode) << shift);
    }

    void release() const noexcept { port_->BSRR = mask(); }
    void pull_low() const noexcept { port_->BSRR = mask() << 16U; }  /* старша половина BSRR скидає */

    [[nodiscard]] bool high() const noexcept { return (port_->IDR & mask()) != 0U; }

private:
    [[nodiscard]] constexpr std::uint32_t mask() const noexcept { return 1U << pin_; }

    GPIO_TypeDef* port_;
    unsigned pin_;
};

/* Штатна розкладка I2C1 на STM32F103 */
inline constexpr OpenDrainPin i2c1_scl{GPIOB, 6};
inline constexpr OpenDrainPin i2c1_sda{GPIOB, 7};

} // namespace hw

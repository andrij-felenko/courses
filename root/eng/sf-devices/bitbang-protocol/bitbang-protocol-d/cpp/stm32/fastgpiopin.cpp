#include "stm32f4xx.h"
#include <stdint.h>
#include <type_traits>

// Клас для статичного опису виводу GPIO з нульовою вартістю абстракції
template <uintptr_t PortAddress, uint8_t PinIndex>
struct FastGpioPin {
    static_assert(PinIndex < 16, "Pin index must be 0-15");
    static constexpr GPIO_TypeDef* port = reinterpret_cast<GPIO_TypeDef*>(PortAddress);
    static constexpr uint16_t pin_mask  = static_cast<uint16_t>(1U << PinIndex);

    static inline void set_high() noexcept __attribute__((always_inline)) {
        port->BSRR = pin_mask;
    }

    static inline void set_low() noexcept __attribute__((always_inline)) {
        port->BSRR = static_cast<uint32_t>(pin_mask) << 16;
    }

    static inline bool read() noexcept __attribute__((always_inline)) {
        return (port->IDR & pin_mask) != 0;
    }
};

// RAII обгортка для захисту критичної секції
class CriticalSectionGuard {
public:
    inline CriticalSectionGuard() noexcept : primask_(__get_PRIMASK()) {
        __disable_irq();
    }
    inline ~CriticalSectionGuard() noexcept {
        if (!primask_) {
            __enable_irq();
        }
    }
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;

private:
    uint32_t primask_;
};

// Шаблонований модуль Bit-bang SPI з нульовими накладними витратами
template <typename SckPin, typename MosiPin, typename MisoPin>
class BitBangSpiMasterFast {
public:
    static inline uint8_t transfer_byte(uint8_t tx_data) noexcept __attribute__((always_inline)) {
        uint8_t rx_data = 0;

        // Вхід у критичну секцію через RAII
        CriticalSectionGuard lock;

        // Метапрограмування: компілятор розгортає цикл і повністю прибирає розгалуження
        unroll_bit_transfer<7>(tx_data, rx_data);

        return rx_data;
    }

private:
    template <int8_t BitIndex>
    static inline void unroll_bit_transfer(uint8_t tx_data, uint8_t& rx_data) noexcept __attribute__((always_inline)) {
        if ((tx_data >> BitIndex) & 0x01) {
            MosiPin::set_high();
        } else {
            MosiPin::set_low();
        }

        asm volatile("" ::: "memory");
        SckPin::set_high();

        if (MisoPin::read()) {
            rx_data |= static_cast<uint8_t>(1U << BitIndex);
        }

        SckPin::set_low();
        asm volatile("" ::: "memory");

        if constexpr (BitIndex > 0) {
            unroll_bit_transfer<BitIndex - 1>(tx_data, rx_data);
        }
    }
};

// Приклад створення драйвера для конкретної конфігурації ніжок:
using Sck  = FastGpioPin<GPIOA_BASE, 5>;
using Mosi = FastGpioPin<GPIOA_BASE, 7>;
using Miso = FastGpioPin<GPIOA_BASE, 6>;
using SpiDriver = BitBangSpiMasterFast<Sck, Mosi, Miso>;

#include "stm32f4xx.h"
#include <stdint.h>

// Шаблонована C++ абстракція для нульових накладних витрат (Zero-Cost Abstraction)
template <uint32_t GPIO_BASE, uint8_t PIN_NUM>
struct GpioPin {
    static constexpr GPIO_TypeDef* port() { return reinterpret_cast<GPIO_TypeDef*>(GPIO_BASE); }
    static constexpr uint32_t mask() { return (1U << PIN_NUM); }

    static inline void set_high() __attribute__((always_inline)) {
        port()->BSRR = mask();
    }

    static inline void set_low() __attribute__((always_inline)) {
        port()->BSRR = (mask() << 16);
    }

    static inline bool read() __attribute__((always_inline)) {
        return (port()->IDR & mask()) != 0;
    }
};

// Клас драйвера Bit-bang SPI з інлайнінгом інструкцій
template <typename SckPin, typename MosiPin, typename MisoPin>
class BitBangSpiMaster {
public:
    static inline void init() {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CYCCNT = 0;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        SckPin::set_low();
        MosiPin::set_low();
    }

    static inline uint8_t transfer(uint8_t tx_data, uint32_t delay_ticks) __attribute__((always_inline)) {
        uint8_t rx_data = 0;
        
        uint32_t primask = __get_PRIMASK();
        __disable_irq();

        for (int8_t bit = 7; bit >= 0; --bit) {
            if (tx_data & (1U << bit)) {
                MosiPin::set_high();
            } else {
                MosiPin::set_low();
            }

            delay(delay_ticks);
            SckPin::set_high();
            delay(delay_ticks);

            if (MisoPin::read()) {
                rx_data |= (1U << bit);
            }

            SckPin::set_low();
            delay(delay_ticks);
        }

        if (!primask) {
            __enable_irq();
        }

        return rx_data;
    }

private:
    static inline void delay(uint32_t ticks) __attribute__((always_inline)) {
        uint32_t start = DWT->CYCCNT;
        while ((DWT->CYCCNT - start) < ticks) {
            asm volatile("nop");
        }
    }
};

// Приклад використання C++ драйвера Bit-bang SPI:
// Using GPIOA, Pin 5 (SCK), Pin 7 (MOSI), Pin 6 (MISO)
using Sck  = GpioPin<GPIOA_BASE, 5>;
using Mosi = GpioPin<GPIOA_BASE, 7>;
using Miso = GpioPin<GPIOA_BASE, 6>;
using SpiDriver = BitBangSpiMaster<Sck, Mosi, Miso>;

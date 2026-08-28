// Реалізація HAL для STM32 мовою C++ у вигляді структури
#include "stm32f4xx.h"

struct Stm32I2cHal {
    static void set_scl_low() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR8;
    }
    static void set_scl_high_z() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS8;
    }
    static bool read_scl() noexcept {
        return (GPIOB->IDR & GPIO_IDR_ID8) != 0;
    }
    static void set_sda_low() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR9;
    }
    static void set_sda_high_z() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS9;
    }
    static bool read_sda() noexcept {
        return (GPIOB->IDR & GPIO_IDR_ID9) != 0;
    }
    static void delay_half_period() noexcept {
        for (volatile uint32_t i = 0; i < 80; ++i) {
            __NOP();
        }
    }
    static uint32_t current_time_us() noexcept {
        return DWT->CYCCNT / (SystemCoreClock / 1000000);
    }
};

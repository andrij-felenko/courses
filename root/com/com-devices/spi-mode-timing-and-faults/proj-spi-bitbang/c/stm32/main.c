/* Високошвидкісний біт-бенгінг на STM32 через регістри прямого бітового доступу BSRR */
#include "stm32f4xx_ll_gpio.h"

#define PIN_SCLK  LL_GPIO_PIN_5
#define PIN_MISO  LL_GPIO_PIN_6
#define PIN_MOSI  LL_GPIO_PIN_7
#define PIN_CS    LL_GPIO_PIN_4
#define SPI_PORT  GPIOA

static inline void set_sclk(bool level) {
    if (level) LL_GPIO_SetOutputPin(SPI_PORT, PIN_SCLK);
    else LL_GPIO_ResetOutputPin(SPI_PORT, PIN_SCLK);
}

static inline void set_mosi(bool level) {
    if (level) LL_GPIO_SetOutputPin(SPI_PORT, PIN_MOSI);
    else LL_GPIO_ResetOutputPin(SPI_PORT, PIN_MOSI);
}

static inline bool get_miso(void) {
    return LL_GPIO_IsInputPinSet(SPI_PORT, PIN_MISO);
}

uint8_t stm32_spi_bb_transfer_byte(uint8_t out, uint8_t mode) {
    bool cpol = (mode == 2 || mode == 3);
    bool cpha = (mode == 1 || mode == 3);
    uint8_t in = 0;

    for (int8_t i = 7; i >= 0; --i) {
        bool bit = (out >> i) & 1;

        if (!cpha) {
            set_mosi(bit);
            __NOP(); __NOP(); __NOP();
            set_sclk(!cpol);
            __NOP(); __NOP(); __NOP();
            if (get_miso()) in |= (1 << i);
            set_sclk(cpol);
        } else {
            set_sclk(!cpol);
            set_mosi(bit);
            __NOP(); __NOP(); __NOP();
            set_sclk(cpol);
            __NOP(); __NOP(); __NOP();
            if (get_miso()) in |= (1 << i);
        }
    }
    return in;
}

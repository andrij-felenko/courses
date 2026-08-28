/* c_gpio_config.c */
#include <stdint.h>

#define GPIOA_BASE  0x40020000UL
#define GPIOA_MODER (*(volatile uint32_t*)(GPIOA_BASE + 0x00))

void configure_pin_c(void) {
    uint32_t val = GPIOA_MODER;
    val &= ~(0x3U << 10); // Очищення бітів 10..11
    val |= (0x1U << 10);  // Встановлення режиму Output (01)
    GPIOA_MODER = val;
}

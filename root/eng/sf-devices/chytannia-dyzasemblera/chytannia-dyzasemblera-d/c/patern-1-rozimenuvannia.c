#include <stdint.h>

#define GPIOA_BASE  0x40020000UL
#define GPIOA_ODR   (*(volatile uint32_t*)(GPIOA_BASE + 0x14))
#define GPIOA_BSRR  (*(volatile uint32_t*)(GPIOA_BASE + 0x18))

void toggle_pin_odr(void) {
    GPIOA_ODR |= (1UL << 5);
}

void set_pin_bsrr(void) {
    GPIOA_BSRR = (1UL << 5);
}

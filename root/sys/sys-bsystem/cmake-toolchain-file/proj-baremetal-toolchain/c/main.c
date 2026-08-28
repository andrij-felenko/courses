/* main.c — процедурний підхід із макросами розіменування адрес */
#include <stdint.h>

#define RCC_AHB1ENR  (*(volatile uint32_t *)0x40023830)
#define GPIOC_MODER  (*(volatile uint32_t *)0x40020800)
#define GPIOC_ODR    (*(volatile uint32_t *)0x40020814)

static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile("nop");
    }
}

void main_app(void) {
    /* Увімкнення тактування порту GPIOC (біт 2) */
    RCC_AHB1ENR |= (1U << 2);

    /* Налаштування піна PC13 на вихід */
    GPIOC_MODER &= ~(3U << (13 * 2));
    GPIOC_MODER |= (1U << (13 * 2));

    while (1) {
        GPIOC_ODR ^= (1U << 13);
        delay_cycles(500000);
    }
}

// main.c — Мінімальний перевірочний Blinky на прямих регістрах CMSIS
#include <stdint.h>

#define RCC_BASE        0x40023800U
#define GPIOA_BASE      0x40020000U

#define RCC_AHB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x30U))
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_ODR       (*(volatile uint32_t *)(GPIOA_BASE + 0x14U))

static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile ("nop");
    }
}

int main(void) {
    // 1. Вмикаємо тактування порту GPIOA (біт 0 в RCC_AHB1ENR)
    RCC_AHB1ENR |= (1U << 0);

    // 2. Налаштовуємо пін PA5 як вихід загального призначення (MODER5 = 0b01)
    GPIOA_MODER &= ~(3U << (5 * 2));
    GPIOA_MODER |=  (1U << (5 * 2));

    // 3. Нескінченний цикл перемикання світлодіода
    while (1) {
        GPIOA_ODR ^= (1U << 5);      // Інвертуємо стан виводу PA5
        delay_cycles(500000U);       // Програмна затримка (~0.5 с на частоті 16 МГц HSI)
    }

    return 0;
}

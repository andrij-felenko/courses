/* Мінімальний Bring-Up тест: перемикання тестового GPIO та активація MCO */
#include <stdint.h>

#define RCC_BASE        0x40023800U
#define GPIOA_BASE      0x40020000U
#define GPIOC_BASE      0x40020800U

#define RCC_AHB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x30U))
#define RCC_CFGR        (*(volatile uint32_t *)(RCC_BASE + 0x08U))

#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_AFRH      (*(volatile uint32_t *)(GPIOA_BASE + 0x24U))

#define GPIOC_MODER     (*(volatile uint32_t *)(GPIOC_BASE + 0x00U))
#define GPIOC_ODR       (*(volatile uint32_t *)(GPIOC_BASE + 0x14U))

static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile ("nop");
    }
}

int main(void) {
    /* 1. Тактування портів GPIOA (для MCO1 на PA8) та GPIOC (для LED на PC13) */
    RCC_AHB1ENR |= (1U << 0) | (1U << 2);

    /* 2. Конфігурація PC13 як вихід (01 у біти MODER13) */
    GPIOC_MODER &= ~(3U << (13 * 2));
    GPIOC_MODER |=  (1U << (13 * 2));

    /* 3. Конфігурація PA8 як альтернативна функція AF0 (MCO1 виводить HSE/HSI) */
    GPIOA_MODER &= ~(3U << (8 * 2));
    GPIOA_MODER |=  (2U << (8 * 2));   /* Alternate Function mode */
    GPIOA_AFRH  &= ~(0xFU << ((8 - 8) * 4)); /* AF0 для MCO1 */

    /* 4. Налаштування MCO1: вивід тактового сигналу з дільником /4 */
    RCC_CFGR &= ~((3U << 21) | (7U << 24));
    RCC_CFGR |=  (0U << 21) | (6U << 24); /* Джерело HSI, дільник /4 */

    /* 5. Нескінченне блимання для підтвердження виконання коду */
    while (1) {
        GPIOC_ODR ^= (1U << 13);
        delay_cycles(200000);
    }

    return 0;
}

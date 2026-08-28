#include <stdint.h>

/* Базові адреси периферійних блоків на шині AHB1 (STM32F4) */
#define PERIPH_BASE           (0x40000000UL)
#define AHB1PERIPH_BASE       (PERIPH_BASE + 0x00020000UL)
#define RCC_BASE              (AHB1PERIPH_BASE + 0x3800UL)
#define GPIOC_BASE            (AHB1PERIPH_BASE + 0x0800UL)

/* Зсуви регістрів RCC */
#define RCC_AHB1ENR_OFFSET    (0x30UL)
#define RCC_AHB1ENR           (*(volatile uint32_t *)(RCC_BASE + RCC_AHB1ENR_OFFSET))
#define RCC_AHB1ENR_GPIOCEN   (1UL << 2)

/* Зсуви регістрів GPIO */
#define GPIO_MODER_OFFSET     (0x00UL)
#define GPIO_OTYPER_OFFSET    (0x04UL)
#define GPIO_OSPEEDR_OFFSET   (0x08UL)
#define GPIO_PUPDR_OFFSET     (0x0CUL)
#define GPIO_BSRR_OFFSET      (0x18UL)

#define GPIOC_MODER           (*(volatile uint32_t *)(GPIOC_BASE + GPIO_MODER_OFFSET))
#define GPIOC_OTYPER          (*(volatile uint32_t *)(GPIOC_BASE + GPIO_OTYPER_OFFSET))
#define GPIOC_OSPEEDR         (*(volatile uint32_t *)(GPIOC_BASE + GPIO_OSPEEDR_OFFSET))
#define GPIOC_PUPDR           (*(volatile uint32_t *)(GPIOC_BASE + GPIO_PUPDR_OFFSET))
#define GPIOC_BSRR            (*(volatile uint32_t *)(GPIOC_BASE + GPIO_BSRR_OFFSET))

#define LED_PIN               (13U)

/* Програмна затримка на змінній volatile */
static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __asm__ volatile ("nop");
    }
}

int main(void) {
    /* 1. Вмикаємо тактування порту GPIOC */
    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOCEN;

    /* Короткий бар'єр пам'яті для стабілізації шини після ввімкнення такту */
    __asm__ volatile ("dmb" ::: "memory");

    /* 2. Налаштовуємо пін 13 як вихід (01 у бітах 27:26) */
    GPIOC_MODER &= ~(3UL << (LED_PIN * 2));
    GPIOC_MODER |=  (1UL << (LED_PIN * 2));

    /* Push-Pull (0 у біті 13) */
    GPIOC_OTYPER &= ~(1UL << LED_PIN);

    /* Низька швидкість Low Speed для зменшення завад (00 у бітах 27:26) */
    GPIOC_OSPEEDR &= ~(3UL << (LED_PIN * 2));

    /* Без внутрішньої підтяжки No Pull (00 у бітах 27:26) */
    GPIOC_PUPDR &= ~(3UL << (LED_PIN * 2));

    /* 3. Головний цикл блимання */
    while (1) {
        /* Вмикаємо світлодіод (для Active High — встановлення біта 13) */
        GPIOC_BSRR = (1UL << LED_PIN);
        delay_cycles(500000);

        /* Вимикаємо світлодіод (скидання біта 13 через старшу половину BSRR) */
        GPIOC_BSRR = (1UL << (LED_PIN + 16));
        delay_cycles(500000);
    }

    return 0;
}

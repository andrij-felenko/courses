#include <stdint.h>
#include <stdbool.h>

// Прямий доступ до базових адрес периферії STM32G4 / STM32F4 (Cortex-M4)
#define RCC_BASE            0x40021000UL
#define RCC_AHB2ENR         (*(volatile uint32_t *)(RCC_BASE + 0x4C))
#define RCC_AHB2ENR_GPIOAEN (1UL << 0)
#define RCC_AHB2ENR_GPIOBEN (1UL << 1)

#define GPIOA_BASE          0x48000000UL
#define GPIOA_MODER         (*(volatile uint32_t *)(GPIOA_BASE + 0x00))
#define GPIOA_OTYPER        (*(volatile uint32_t *)(GPIOA_BASE + 0x04))
#define GPIOA_OSPEEDR       (*(volatile uint32_t *)(GPIOA_BASE + 0x08))
#define GPIOA_PUPDR         (*(volatile uint32_t *)(GPIOA_BASE + 0x0C))
#define GPIOA_BSRR          (*(volatile uint32_t *)(GPIOA_BASE + 0x18))
#define GPIOA_LCKR          (*(volatile uint32_t *)(GPIOA_BASE + 0x1C))

#define GPIOB_BASE          0x48000400UL
#define GPIOB_MODER         (*(volatile uint32_t *)(GPIOB_BASE + 0x00))
#define GPIOB_PUPDR         (*(volatile uint32_t *)(GPIOB_BASE + 0x0C))
#define GPIOB_BSRR          (*(volatile uint32_t *)(GPIOB_BASE + 0x18))

// Конфігурація критичних пінів:
// PA5: Керування нижнім ключем напівмоста (Active-High, безпечний стан = 0)
// PB2: Вхід аварійного термодатчика (Вхід із підтяжкою Pull-Up)

void EarlySystem_Pins_PreInit(void) {
    // 1. Вмикаємо тактування портів GPIO в контролері RCC
    RCC_AHB2ENR |= (RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN);

    // Обов'язкова затримка на 2 такти шини для синхронізації тактового домену AHB
    __asm volatile ("dsb 0xF" ::: "memory");
    volatile uint32_t dummy = RCC_AHB2ENR;
    (void)dummy;

    // 2. БЕЗПЕЧНА ПОПЕРЕДНЯ УСТАНОВКА РІВНЯ:
    // Скидаємо PA5 у логічний 0 через біт BR5 регістра BSRR ДО перемикання режиму MODER
    GPIOA_BSRR = (1UL << (5 + 16)); // Bit Reset PA5

    // 3. Конфігурація підтяжки PUPDR для PA5 (Pull-Down для додаткового захисту)
    GPIOA_PUPDR &= ~(0x3UL << (5 * 2));
    GPIOA_PUPDR |=  (0x2UL << (5 * 2)); // 10b: Pull-Down

    // 4. Перемикаємо PA5 у режим виходу загального призначення (MODER = 01b, Low Speed)
    GPIOA_OSPEEDR &= ~(0x3UL << (5 * 2)); // 00b: Low Speed (мінімізація перешкод)
    GPIOA_MODER   &= ~(0x3UL << (5 * 2));
    GPIOA_MODER   |=  (0x1UL << (5 * 2)); // 01b: Output

    // 5. Конфігурація PB2 як входу з підтяжкою Pull-Up
    GPIOB_MODER &= ~(0x3UL << (2 * 2)); // 00b: Input
    GPIOB_PUPDR &= ~(0x3UL << (2 * 2));
    GPIOB_PUPDR |=  (0x1UL << (2 * 2)); // 01b: Pull-Up

    // 6. Апаратне блокування конфігурації PA5 через регістр LCKR
    uint32_t lock_mask = (1UL << 5);
    GPIOA_LCKR = lock_mask | (1UL << 16); // Крок 1: LCKK = 1
    GPIOA_LCKR = lock_mask;               // Крок 2: LCKK = 0
    GPIOA_LCKR = lock_mask | (1UL << 16); // Крок 3: LCKK = 1
    (void)GPIOA_LCKR;                     // Крок 4: Читання
    (void)GPIOA_LCKR;                     // Крок 5: Підтвердження блокування
}

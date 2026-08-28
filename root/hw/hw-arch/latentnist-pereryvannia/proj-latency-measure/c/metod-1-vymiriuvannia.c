#include <stdint.h>
#include <stdbool.h>

/* Адреси базових регістрів для STM32F4 (AHB1: GPIOA, APB2: SYSCFG/EXTI) */
#define RCC_AHB1ENR   (*(volatile uint32_t *)0x40023830U)
#define RCC_APB2ENR   (*(volatile uint32_t *)0x40023844U)

#define GPIOA_MODER   (*(volatile uint32_t *)0x40020000U)
#define GPIOA_OSPEEDR (*(volatile uint32_t *)0x40020008U)
#define GPIOA_BSRR    (*(volatile uint32_t *)0x40020018U)

#define SYSCFG_EXTICR1 (*(volatile uint32_t *)0x40013808U)
#define EXTI_IMR      (*(volatile uint32_t *)0x40013C00U)
#define EXTI_RTSR     (*(volatile uint32_t *)0x40013C08U)
#define EXTI_PR       (*(volatile uint32_t *)0x40013C14U)

#define NVIC_ISER0    (*(volatile uint32_t *)0xE000E100U)

/* Ініціалізація виводів: PA0 (вхід EXTI), PA1 (надшвидкий вихід) */
void latency_gpio_init(void) {
    /* Вмикаємо тактування GPIOA та SYSCFG */
    RCC_AHB1ENR |= (1U << 0);
    RCC_APB2ENR |= (1U << 14);

    /* PA0: вхід (MODER[1:0] = 00) */
    GPIOA_MODER &= ~(3U << 0);

    /* PA1: вихід (MODER[3:2] = 01) з максимальною швидкістю (OSPEEDR[3:2] = 11) */
    GPIOA_MODER &= ~(3U << 2);
    GPIOA_MODER |= (1U << 2);
    GPIOA_OSPEEDR |= (3U << 2);

    /* Скидаємо PA1 в низький рівень */
    GPIOA_BSRR = (1U << (1 + 16));

    /* Налаштовуємо EXTI0 на лінію PA0 */
    SYSCFG_EXTICR1 &= ~0x000FU;

    /* Дозволяємо переривання по лінії 0 та вибираємо наростаючий фронт */
    EXTI_IMR |= (1U << 0);
    EXTI_RTSR |= (1U << 0);

    /* Дозволяємо вектор EXTI0 (IRQn = 6) у NVIC */
    NVIC_ISER0 = (1U << 6);
}

/* Обробник переривання EXTI0 */
void EXTI0_IRQHandler(void) {
    /* НАЙПЕРША ІНСТРУКЦІЯ: миттєво піднімаємо PA1 у логічну 1 через BSRR */
    GPIOA_BSRR = (1U << 1);

    /* Скидаємо прапорець переривання EXTI0 (запис 1 у PR очищає запит) */
    EXTI_PR = (1U << 0);

    /* Опускаємо PA1 назад для формування вимірювального імпульсу */
    GPIOA_BSRR = (1U << (1 + 16));
}

#include <stdint.h>
#include <stdbool.h>

#define GPIOA_MODER_REG   (*(volatile uint32_t *)0x48000000UL)
#define GPIOA_PUPDR_REG   (*(volatile uint32_t *)0x4800000CUL)
#define GPIOA_ODR_REG     (*(volatile uint32_t *)0x48000014UL)

#define GPIOB_MODER_REG   (*(volatile uint32_t *)0x48000400UL)
#define GPIOB_PUPDR_REG   (*(volatile uint32_t *)0x4800040CUL)
#define GPIOB_BSRR_REG    (*(volatile uint32_t *)0x48000418UL)

#define DBGMCU_CR_REG     (*(volatile uint32_t *)0xE0042004UL)

#define PIN_LOAD_SWITCH_PB12 (1U << 12)
#define PIN_WAKEUP_PA0       (1U << 0)

/**
 * @brief Підготовка системи та виводів до переходу в глибокий сон
 */
void board_prepare_for_deep_sleep(void)
{
    /* 1. Ізоляція сигнальних ліній периферійних шин (скидання в 0 В) */
    GPIOA_ODR_REG &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7));

    /* 2. Знеструмлення зовнішніх датчиків розмиканням ключа P-MOSFET (PB12 HIGH) */
    GPIOB_BSRR_REG = PIN_LOAD_SWITCH_PB12;

    /* 3. Переведення всіх вільних пінів порту А в Analog mode (11b), зберігаючи Wakeup пін PA0 */
    GPIOA_MODER_REG = 0xFFFFFFFCUL | (GPIOA_MODER_REG & 0x03UL);
    GPIOA_PUPDR_REG = 0x00000000UL | (GPIOA_PUPDR_REG & 0x03UL);

    /* 4. Порт B: всі піни в Analog mode, крім виходу керування силовим ключем PB12 */
    uint32_t pb12_mask = (3U << (12 * 2));
    GPIOB_MODER_REG = (~pb12_mask) | (1U << (12 * 2)); /* PB12 лишається Output */
    GPIOB_PUPDR_REG = 0x00000000UL;

    /* 5. Вимкнення блоку налагодження ядра, щоб дозволити зупинку тактових генераторів */
    DBGMCU_CR_REG = 0x00000000UL;
}

/**
 * @brief Головний цикл сну
 */
void board_enter_sleep(void)
{
    board_prepare_for_deep_sleep();

    /* Вхід у режим зупинки за інструкцією WFI */
    __asm volatile("wfi");
}

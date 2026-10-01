#include "system_init.h"

/**
 * @file system_init.c
 * @brief Реалізація початкової ініціалізації периферії (GPIO, USART, NVIC)
 *        та налаштування зсуву векторної таблиці VTOR для запуску з-під bootloader.
 */

/* Низькорівневі адреси регістрів STM32F103 */
#define PERIPH_BASE           0x40000000UL
#define APB1PERIPH_BASE       PERIPH_BASE
#define APB2PERIPH_BASE       (PERIPH_BASE + 0x10000UL)
#define AHBPERIPH_BASE        (PERIPH_BASE + 0x20000UL)
#define SCS_BASE              0xE000E000UL

/* Спеціальний регістр SCB VTOR */
#define SCB_VTOR              (*(volatile uint32_t *)(SCS_BASE + 0x0D08UL))

/* Регістри системного тактування RCC */
#define RCC_BASE              (AHBPERIPH_BASE + 0x1000UL)
#define RCC_CR                (*(volatile uint32_t *)(RCC_BASE + 0x00UL))
#define RCC_CFGR              (*(volatile uint32_t *)(RCC_BASE + 0x04UL))
#define RCC_APB2ENR           (*(volatile uint32_t *)(RCC_BASE + 0x18UL))
#define RCC_APB1ENR           (*(volatile uint32_t *)(RCC_BASE + 0x1CUL))

/* Регістри контролера Flash-пам'яті */
#define FLASH_R_BASE          (AHBPERIPH_BASE + 0x2000UL)
#define FLASH_ACR             (*(volatile uint32_t *)(FLASH_R_BASE + 0x00UL))

/* Порти GPIO */
#define GPIOA_BASE            (APB2PERIPH_BASE + 0x0800UL)
#define GPIOB_BASE            (APB2PERIPH_BASE + 0x0C00UL)
#define GPIOC_BASE            (APB2PERIPH_BASE + 0x1000UL)

#define GPIOA_CRL             (*(volatile uint32_t *)(GPIOA_BASE + 0x00UL))
#define GPIOA_CRH             (*(volatile uint32_t *)(GPIOA_BASE + 0x04UL))
#define GPIOA_BSRR            (*(volatile uint32_t *)(GPIOA_BASE + 0x10UL))

#define GPIOB_CRL             (*(volatile uint32_t *)(GPIOB_BASE + 0x00UL))
#define GPIOB_CRH             (*(volatile uint32_t *)(GPIOB_BASE + 0x04UL))

#define GPIOC_CRH             (*(volatile uint32_t *)(GPIOC_BASE + 0x04UL))

/* Регістри NVIC */
#define NVIC_ISER0            (*(volatile uint32_t *)(SCS_BASE + 0x0100UL))
#define NVIC_IPR9             (*(volatile uint8_t  *)(SCS_BASE + 0x0400UL + 37UL))

/* Бітові маски RCC */
#define RCC_CR_HSEON          (1UL << 16)
#define RCC_CR_HSERDY         (1UL << 17)
#define RCC_CR_PLLON          (1UL << 24)
#define RCC_CR_PLLRDY         (1UL << 25)

#define RCC_CFGR_PLLSRC_HSE   (1UL << 16)
#define RCC_CFGR_PLLMULL9     (0x7UL << 18)
#define RCC_CFGR_PPRE1_DIV2   (0x4UL << 8)
#define RCC_CFGR_SW_PLL       (0x2UL << 0)
#define RCC_CFGR_SWS_PLL      (0x2UL << 2)

#define RCC_APB2ENR_IOPAEN    (1UL << 2)
#define RCC_APB2ENR_IOPBEN    (1UL << 3)
#define RCC_APB2ENR_IOPCEN    (1UL << 4)
#define RCC_APB2ENR_AFIOEN    (1UL << 0)
#define RCC_APB2ENR_USART1EN  (1UL << 14)

void system_vtor_config(uint32_t offset) {
    /* Очищення прапорців та запис вирівняної адреси таблиці векторів переривань */
    SCB_VTOR = (FLASH_BASE_ADDR | (offset & 0x1FFFFF80UL));
}

void system_clock_config(void) {
    /* 1. Увімкнення зовнішнього кварцового резонатора HSE (8 МГц) */
    RCC_CR |= RCC_CR_HSEON;
    while (!(RCC_CR & RCC_CR_HSERDY)) {
        /* Очікування стабілізації HSE */
    }

    /* 2. Конфігурація затримки Flash (2 cycles для частоти > 48 МГц) */
    FLASH_ACR |= 0x02UL;

    /* 3. Налаштування дільників шин: AHB = 1, APB1 = /2 (36 МГц max), APB2 = /1 */
    RCC_CFGR |= RCC_CFGR_PPRE1_DIV2;

    /* 4. Конфігурація PLL: джерело HSE (8 МГц) * 9 = 72 МГц */
    RCC_CFGR |= (RCC_CFGR_PLLSRC_HSE | RCC_CFGR_PLLMULL9);

    /* 5. Увімкнення PLL та очікування готовності */
    RCC_CR |= RCC_CR_PLLON;
    while (!(RCC_CR & RCC_CR_PLLRDY)) {
        /* Очікування захоплення частоти PLL */
    }

    /* 6. Перемикання системного тактування SYSCLK на джерело PLL */
    RCC_CFGR |= RCC_CFGR_SW_PLL;
    while ((RCC_CFGR & (0x3UL << 2)) != RCC_CFGR_SWS_PLL) {
        /* Очікування підтвердження перемикання */
    }
}

void system_gpio_config(void) {
    /* Увімкнення тактування портів GPIOA, GPIOB, GPIOC та альтернативних функцій AFIO */
    RCC_APB2ENR |= (RCC_APB2ENR_IOPAEN | RCC_APB2ENR_IOPBEN | RCC_APB2ENR_IOPCEN | RCC_APB2ENR_AFIOEN);

    /* 
     * Конфігурація ліній SWD на порту GPIOB:
     * PB13 - SWCLK (Output Push-Pull 50MHz, CNF=00, MODE=11)
     * PB14 - SWDIO (Output Push-Pull 50MHz, CNF=00, MODE=11)
     * PB15 - nRESET (Output Open-Drain 50MHz, CNF=01, MODE=11)
     */
    GPIOB_CRH &= ~((0xFUL << 20) | (0xFUL << 24) | (0xFUL << 28));
    GPIOB_CRH |=  ((0x3UL << 20) | (0x3UL << 24) | (0x7UL << 28));

    /*
     * Конфігурація CDC UART (USART1) на порту GPIOA:
     * PA9  - TX (Alternate Function Push-Pull 50MHz, CNF=10, MODE=11)
     * PA10 - RX (Input Floating, CNF=01, MODE=00)
     */
    GPIOA_CRH &= ~((0xFUL << 4) | (0xFUL << 8));
    GPIOA_CRH |=  ((0xBUL << 4) | (0x4UL << 8));

    /*
     * Конфігурація світлодіода індикації стану на PC13:
     * PC13 - Output Push-Pull 2MHz (CNF=00, MODE=10)
     */
    GPIOC_CRH &= ~(0xFUL << 20);
    GPIOC_CRH |=  (0x2UL << 20);
}

void system_nvic_config(void) {
    /* Встановлення пріоритету переривання USART1 (IRQ 37) та його активація */
    NVIC_IPR9 = 0x20; /* Середній пріоритет */
    NVIC_ISER0 |= (1UL << (37 & 0x1F));
}

void system_init_all(void) {
    system_vtor_config(BOOTLOADER_VTOR_OFFSET);
    system_clock_config();
    system_gpio_config();
    system_nvic_config();
}

#ifndef BSP_STM32F4_REGS_H
#define BSP_STM32F4_REGS_H

#include <stdint.h>

/*
 * Мінімальна карта периферії STM32F42x/43x (кварц 8 МГц, SYSCLK 168 МГц).
 * Тільки те, що потрібне тактовому дереву: RCC, FLASH, PWR, GPIOA, гальмо
 * ШІМ-виходів TIM1 і регістр скидання ядра. Жодних сторонніх бібліотек —
 * самі адреси й бітові поля з довідника на мікроконтролер.
 */

typedef struct {
    volatile uint32_t CR;             /* 0x00 керування генераторами HSI/HSE/PLL/CSS */
    volatile uint32_t PLLCFGR;        /* 0x04 дільники контуру PLL */
    volatile uint32_t CFGR;           /* 0x08 мультиплексор SYSCLK, переддільники шин, MCO */
    volatile uint32_t CIR;            /* 0x0C прапорці й дозволи переривань тактування */
    volatile uint32_t RESERVED0[8];   /* 0x10..0x2C регістри скидання шин — не чіпаємо */
    volatile uint32_t AHB1ENR;        /* 0x30 тактування AHB1 (порти GPIO) */
    volatile uint32_t AHB2ENR;        /* 0x34 */
    volatile uint32_t AHB3ENR;        /* 0x38 */
    volatile uint32_t RESERVED1;      /* 0x3C */
    volatile uint32_t APB1ENR;        /* 0x40 тактування APB1 (тут живе інтерфейс PWR) */
    volatile uint32_t APB2ENR;        /* 0x44 */
} rcc_regs_t;

typedef struct {
    volatile uint32_t ACR;            /* 0x00 такти очікування, префетч, кеші */
} flash_regs_t;

typedef struct {
    volatile uint32_t CR;             /* 0x00 керування регулятором напруги ядра */
    volatile uint32_t CSR;            /* 0x04 статус регулятора (VOSRDY) */
} pwr_regs_t;

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} gpio_regs_t;

#define RCC     ((rcc_regs_t   *)0x40023800UL)
#define FLASH   ((flash_regs_t *)0x40023C00UL)
#define PWR     ((pwr_regs_t   *)0x40007000UL)
#define GPIOA   ((gpio_regs_t  *)0x40020000UL)

/* TIM1_BDTR: біт MOE одним записом гасить усі шість ШІМ-виходів силового мосту */
#define TIM1_BDTR               (*(volatile uint32_t *)(0x40010000UL + 0x44UL))
#define TIM_BDTR_MOE            (1UL << 15)

/* Програмне скидання ядра Cortex-M4 через SCB->AIRCR */
#define SCB_AIRCR               (*(volatile uint32_t *)0xE000ED0CUL)
#define SCB_AIRCR_SYSRESETREQ   0x05FA0004UL

/* --- RCC_CR --- */
#define RCC_CR_HSION            (1UL << 0)
#define RCC_CR_HSIRDY           (1UL << 1)
#define RCC_CR_HSEON            (1UL << 16)
#define RCC_CR_HSERDY           (1UL << 17)
#define RCC_CR_HSEBYP           (1UL << 18)
#define RCC_CR_CSSON            (1UL << 19)
#define RCC_CR_PLLON            (1UL << 24)
#define RCC_CR_PLLRDY           (1UL << 25)

/* --- RCC_PLLCFGR --- */
#define RCC_PLLCFGR_PLLM_SHIFT  0
#define RCC_PLLCFGR_PLLN_SHIFT  6
#define RCC_PLLCFGR_PLLP_SHIFT  16
#define RCC_PLLCFGR_PLLSRC_HSE  (1UL << 22)
#define RCC_PLLCFGR_PLLQ_SHIFT  24

/* --- RCC_CFGR --- */
#define RCC_CFGR_SW_MASK        (3UL << 0)
#define RCC_CFGR_SW_HSI         (0UL << 0)
#define RCC_CFGR_SW_PLL         (2UL << 0)
#define RCC_CFGR_SWS_MASK       (3UL << 2)
#define RCC_CFGR_SWS_HSI        (0UL << 2)
#define RCC_CFGR_SWS_PLL        (2UL << 2)
#define RCC_CFGR_HPRE_MASK      (0xFUL << 4)
#define RCC_CFGR_HPRE_DIV1      (0UL << 4)
#define RCC_CFGR_PPRE1_MASK     (7UL << 10)
#define RCC_CFGR_PPRE1_DIV1     (0UL << 10)
#define RCC_CFGR_PPRE1_DIV4     (5UL << 10)
#define RCC_CFGR_PPRE2_MASK     (7UL << 13)
#define RCC_CFGR_PPRE2_DIV1     (0UL << 13)
#define RCC_CFGR_PPRE2_DIV2     (4UL << 13)
#define RCC_CFGR_MCO1_MASK      (3UL << 21)
#define RCC_CFGR_MCO1_PLL       (3UL << 21)
#define RCC_CFGR_MCO1PRE_MASK   (7UL << 24)
#define RCC_CFGR_MCO1PRE_DIV4   (6UL << 24)

/* --- RCC_CIR --- */
#define RCC_CIR_CSSF            (1UL << 7)
#define RCC_CIR_CSSC            (1UL << 23)

/* --- RCC_AHB1ENR / RCC_APB1ENR --- */
#define RCC_AHB1ENR_GPIOAEN     (1UL << 0)
#define RCC_APB1ENR_PWREN       (1UL << 28)

/* --- FLASH_ACR --- */
#define FLASH_ACR_LATENCY_MASK  (7UL << 0)
#define FLASH_ACR_PRFTEN        (1UL << 8)
#define FLASH_ACR_ICEN          (1UL << 9)
#define FLASH_ACR_DCEN          (1UL << 10)
#define FLASH_ACR_ICRST         (1UL << 11)
#define FLASH_ACR_DCRST         (1UL << 12)

/* --- PWR_CR / PWR_CSR --- */
#define PWR_CR_VOS_MASK         (3UL << 14)
#define PWR_CR_VOS_SCALE1       (3UL << 14)   /* 1.2 В — потрібно для 168 МГц */
#define PWR_CR_VOS_SCALE3       (1UL << 14)   /* найощадніший режим, до 120 МГц */
#define PWR_CSR_VOSRDY          (1UL << 14)

#endif /* BSP_STM32F4_REGS_H */

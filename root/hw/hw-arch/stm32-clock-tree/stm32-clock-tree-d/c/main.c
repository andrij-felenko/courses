#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів перифірії STM32F4xx */
#define RCC_BASE        0x40023800U
#define FLASH_R_BASE    0x40023C00U
#define PWR_BASE        0x40007000U

/* Структури регістрів безпосереднього відображення в пам'ять */
typedef struct {
    volatile uint32_t CR;            /* 0x00: Clock control register */
    volatile uint32_t PLLCFGR;       /* 0x04: PLL configuration register */
    volatile uint32_t CFGR;          /* 0x08: Clock configuration register */
    volatile uint32_t CIR;           /* 0x0C: Clock interrupt register */
    volatile uint32_t AHB1RSTR;      /* 0x10: AHB1 peripheral reset */
    volatile uint32_t AHB2RSTR;      /* 0x14: AHB2 peripheral reset */
    volatile uint32_t AHB3RSTR;      /* 0x18: AHB3 peripheral reset */
    uint32_t RESERVED0;
    volatile uint32_t APB1RSTR;      /* 0x20: APB1 peripheral reset */
    volatile uint32_t APB2RSTR;      /* 0x24: APB2 peripheral reset */
    uint32_t RESERVED1[2];
    volatile uint32_t AHB1ENR;       /* 0x30: AHB1 peripheral clock enable */
    volatile uint32_t AHB2ENR;       /* 0x34: AHB2 peripheral clock enable */
    volatile uint32_t AHB3ENR;       /* 0x38: AHB3 peripheral clock enable */
    uint32_t RESERVED2;
    volatile uint32_t APB1ENR;       /* 0x40: APB1 peripheral clock enable */
    volatile uint32_t APB2ENR;       /* 0x44: APB2 peripheral clock enable */
} RCC_TypeDef;

typedef struct {
    volatile uint32_t ACR;           /* 0x00: Flash access control register */
    volatile uint32_t KEYR;          /* 0x04: Flash key register */
    volatile uint32_t OPTKEYR;       /* 0x08: Flash option key register */
    volatile uint32_t SR;            /* 0x0C: Flash status register */
    volatile uint32_t CR;            /* 0x10: Flash control register */
    volatile uint32_t OPTCR;         /* 0x14: Flash option control register */
} FLASH_TypeDef;

typedef struct {
    volatile uint32_t CR;            /* 0x00: Power control register */
    volatile uint32_t CSR;           /* 0x04: Power control/status register */
} PWR_TypeDef;

#define RCC_DEV   ((RCC_TypeDef *)RCC_BASE)
#define FLASH_DEV ((FLASH_TypeDef *)FLASH_R_BASE)
#define PWR_DEV   ((PWR_TypeDef *)PWR_BASE)

/* Бітові маски регістрів RCC */
#define RCC_CR_HSEON_BIT       (1U << 16)
#define RCC_CR_HSERDY_BIT      (1U << 17)
#define RCC_CR_PLLON_BIT       (1U << 24)
#define RCC_CR_PLLRDY_BIT      (1U << 25)
#define RCC_CR_CSSON_BIT       (1U << 19)

#define RCC_PLLCFGR_SRC_HSE    (1U << 22)
#define RCC_CFGR_SW_PLL        (2U << 0)
#define RCC_CFGR_SWS_PLL       (2U << 2)
#define RCC_CFGR_SWS_MASK      (3U << 2)

#define RCC_CFGR_HPRE_DIV1     (0U << 4)
#define RCC_CFGR_PPRE1_DIV4    (5U << 10)  /* Дільник /4 для APB1 (101b) */
#define RCC_CFGR_PPRE2_DIV2    (4U << 13)  /* Дільник /2 для APB2 (100b) */

#define RCC_APB1ENR_PWREN_BIT  (1U << 28)
#define PWR_CR_VOS_SCALE1      (1U << 14)

#define FLASH_ACR_LATENCY_5WS  (5U << 0)
#define FLASH_ACR_PRFTEN_BIT   (1U << 8)
#define FLASH_ACR_ICEN_BIT     (1U << 9)
#define FLASH_ACR_DCEN_BIT     (1U << 10)

typedef enum {
    CLOCK_OK = 0,
    CLOCK_ERR_HSE_TIMEOUT,
    CLOCK_ERR_PLL_TIMEOUT,
    CLOCK_ERR_SW_TIMEOUT
} ClockStatus;

/**
 * @brief  Налаштування STM32F4 на максимальну тактову частоту 168 МГц від 8 МГц кварцу
 * @return Результат ініціалізації (CLOCK_OK або код помилки)
 */
ClockStatus SystemClock_Config_168MHz(void)
{
    uint32_t timeout;

    /* 1. Запуск зовнішнього високочастотного кварцу HSE */
    RCC_DEV->CR |= RCC_CR_HSEON_BIT;

    timeout = 200000U;
    while (!(RCC_DEV->CR & RCC_CR_HSERDY_BIT)) {
        if (--timeout == 0U) {
            return CLOCK_ERR_HSE_TIMEOUT; /* Кварц не запустився */
        }
    }

    /* 2. Увімкнення тактування блоку PWR та вибір регулятора напруги Scale 1 */
    RCC_DEV->APB1ENR |= RCC_APB1ENR_PWREN_BIT;
    PWR_DEV->CR |= PWR_CR_VOS_SCALE1;

    /* 3. Конфігурація затримок Flash: 5 WS + Prefetch + Кеш інструкцій та даних */
    FLASH_DEV->ACR = FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT |
                     FLASH_ACR_PRFTEN_BIT | FLASH_ACR_LATENCY_5WS;

    /* 4. Конфігурація дільників шин: AHB = /1 (168 МГц), APB1 = /4 (42 МГц), APB2 = /2 (84 МГц) */
    RCC_DEV->CFGR &= ~((0x0FU << 4) | (7U << 10) | (7U << 13));
    RCC_DEV->CFGR |= (RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2);

    /* 5. Налаштування дільників та множників PLL:
     *    f_IN = 8 МГц, M = 8 -> f_VCO_IN = 1 МГц
     *    N = 336            -> f_VCO_OUT = 336 МГц
     *    P = 2 (код 00b)    -> f_SYSCLK = 336 / 2 = 168 МГц
     *    Q = 7              -> f_USB = 336 / 7 = 48 МГц
     */
    const uint32_t pll_m = 8U;
    const uint32_t pll_n = 336U;
    const uint32_t pll_p_bits = 0U; /* 00b відповідає діленню на 2 */
    const uint32_t pll_q = 7U;

    RCC_DEV->PLLCFGR = (pll_m << 0) |
                       (pll_n << 6) |
                       (pll_p_bits << 16) |
                       RCC_PLLCFGR_SRC_HSE |
                       (pll_q << 24);

    /* 6. Увімкнення головного помножувача PLL */
    RCC_DEV->CR |= RCC_CR_PLLON_BIT;

    timeout = 200000U;
    while (!(RCC_DEV->CR & RCC_CR_PLLRDY_BIT)) {
        if (--timeout == 0U) {
            return CLOCK_ERR_PLL_TIMEOUT; /* PLL не зафіксував фазу */
        }
    }

    /* 7. Комутація системного тактового сигналу на вихід PLL */
    RCC_DEV->CFGR &= ~3U;
    RCC_DEV->CFGR |= RCC_CFGR_SW_PLL;

    /* 8. Очікування підтвердження перемикання джерела (SWS == 10b) */
    timeout = 200000U;
    while ((RCC_DEV->CFGR & RCC_CFGR_SWS_MASK) != RCC_CFGR_SWS_PLL) {
        if (--timeout == 0U) {
            return CLOCK_ERR_SW_TIMEOUT;
        }
    }

    /* 9. Активація захисної системи тактування CSS (Clock Security System) */
    RCC_DEV->CR |= RCC_CR_CSSON_BIT;

    return CLOCK_OK;
}

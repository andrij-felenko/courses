#include <stdint.h>
#include <stdbool.h>

#define FLASH_ACR_REG     (*(volatile uint32_t *)0x40023C00U)
#define RCC_CR_REG        (*(volatile uint32_t *)0x40023800U)
#define RCC_CFGR_REG      (*(volatile uint32_t *)0x40023808U)

#define FLASH_ACR_LATENCY_5WS (5U)
#define FLASH_ACR_PRFTEN      (1U << 8)
#define FLASH_ACR_ICEN        (1U << 9)
#define FLASH_ACR_DCEN        (1U << 10)

#define RCC_CR_PLLON          (1U << 24)
#define RCC_CR_PLLRDY         (1U << 25)
#define RCC_CFGR_SW_PLL       (2U)
#define RCC_CFGR_SWS_MASK     (0x0CU)
#define RCC_CFGR_SWS_PLL      (0x08U)

/* Безпечний перехід на високу частоту 168 МГц */
bool system_clock_scale_up_168mhz(void) {
    /* 1. СПЕРШУ збільшуємо затримку Flash до 5WS та вмикаємо кеші */
    FLASH_ACR_REG = FLASH_ACR_LATENCY_5WS | FLASH_ACR_PRFTEN | 
                    FLASH_ACR_ICEN | FLASH_ACR_DCEN;

    /* 2. Очікуємо фіксації затримки 5WS */
    uint32_t timeout = 5000U;
    while ((FLASH_ACR_REG & 0x0FU) != FLASH_ACR_LATENCY_5WS) {
        if (--timeout == 0U) return false;
    }

    /* 3. Запускаємо PLL (передбачається, що дільники PLLM/PLLN/PLLP вже налаштовані) */
    RCC_CR_REG |= RCC_CR_PLLON;
    timeout = 10000U;
    while (!(RCC_CR_REG & RCC_CR_PLLRDY)) {
        if (--timeout == 0U) return false;
    }

    /* 4. Перемикаємо системний такт на вихід PLL */
    uint32_t cfgr = RCC_CFGR_REG;
    cfgr &= ~0x03U;
    cfgr |= RCC_CFGR_SW_PLL;
    RCC_CFGR_REG = cfgr;

    /* 5. Очікуємо підтвердження перемикання джерела тактування */
    timeout = 5000U;
    while ((RCC_CFGR_REG & RCC_CFGR_SWS_MASK) != RCC_CFGR_SWS_PLL) {
        if (--timeout == 0U) return false;
    }

    return true;
}

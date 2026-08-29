#include "dvfs.h"
#include "stm32f4_regs.h"

clock_status_t dvfs_enter_low_power(void)
{
    clock_status_t st;

    /* 1. Спершу мультиплексор. Поки ядро живиться з PLL, чіпати ні сам PLL,
       ні затримки Flash не можна: інструкцію просто нічим буде вичитати */
    RCC->CR |= RCC_CR_HSION;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_HSIRDY, RCC_CR_HSIRDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        return CLOCK_ERR_HSI_TIMEOUT;
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_MASK) | RCC_CFGR_SW_HSI;
    if (!clock_wait_masked(&RCC->CFGR, RCC_CFGR_SWS_MASK, RCC_CFGR_SWS_HSI,
                           CLOCK_TIMEOUT_CYCLES)) {
        return CLOCK_ERR_SWITCH_TIMEOUT;
    }
    clock_notify_sysclk(CLOCK_HSI_HZ);

    /* 2. Шини на /1: на 16 МГц дільники APB лише крали б периферії частоту */
    clock_set_bus_prescalers(RCC_CFGR_HPRE_DIV1, RCC_CFGR_PPRE1_DIV1, RCC_CFGR_PPRE2_DIV1);

    /* 3. Контур PLL більше нікого не тактує — гасимо його, це десятки мікроампер.
       HSE лишаємо крутитися: повернення на повну швидкість тоді коштує
       мікросекунди замість мілісекунд, і монітор CSS лишається чинним */
    RCC->CR &= ~RCC_CR_PLLON;
    (void)clock_wait_masked(&RCC->CR, RCC_CR_PLLRDY, 0UL, CLOCK_TIMEOUT_CYCLES);

    /* 4. Аж тепер зменшуємо затримки Flash і скидаємо кеші, щоб у них
       не лишилося рядків, прочитаних за старими таймінгами */
    st = clock_set_flash_latency(CLOCK_FLASH_WS_16MHZ);
    if (st != CLOCK_OK) {
        return st;
    }
    clock_reset_flash_caches();

    /* 5. Останнім опускаємо напругу ядра — це дозволено лише при вимкненому PLL */
    return clock_set_voltage_scale(PWR_CR_VOS_SCALE3);
}

clock_status_t dvfs_enter_full_speed(void)
{
    clock_status_t st;

    /* 1. Напруга ядра — перша: розганяти кремній на 1.0 В не можна */
    st = clock_set_voltage_scale(PWR_CR_VOS_SCALE1);
    if (st != CLOCK_OK) {
        return st;
    }

    /* 2. Затримки Flash піднімаємо ще на 16 МГц: зайві такти очікування
       на низькій частоті нічого не ламають, брак їх на високій — ламає все */
    st = clock_set_flash_latency(CLOCK_FLASH_WS_168MHZ);
    if (st != CLOCK_OK) {
        return st;
    }

    /* 3. Кварц ми не гасили, але після зриву CSS його могло вже не бути */
    RCC->CR |= RCC_CR_HSEON;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_HSERDY, RCC_CR_HSERDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        clock_fallback_to_hsi();
        return CLOCK_ERR_HSE_TIMEOUT;
    }

    /* 4. Дільники шин — до підняття SYSCLK */
    clock_set_bus_prescalers(RCC_CFGR_HPRE_DIV1, RCC_CFGR_PPRE1_DIV4, RCC_CFGR_PPRE2_DIV2);

    /* 5. Контур PLL: коефіцієнти в PLLCFGR лишилися з ініціалізації */
    RCC->CR |= RCC_CR_PLLON;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_PLLRDY, RCC_CR_PLLRDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        RCC->CR &= ~RCC_CR_PLLON;
        return CLOCK_ERR_PLL_TIMEOUT;
    }

    /* 6. І тільки тепер перемикаємо мультиплексор на вихід PLL */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_MASK) | RCC_CFGR_SW_PLL;
    if (!clock_wait_masked(&RCC->CFGR, RCC_CFGR_SWS_MASK, RCC_CFGR_SWS_PLL,
                           CLOCK_TIMEOUT_CYCLES)) {
        clock_fallback_to_hsi();
        return CLOCK_ERR_SWITCH_TIMEOUT;
    }

    clock_notify_sysclk(CLOCK_PLL_HZ);
    return CLOCK_OK;
}

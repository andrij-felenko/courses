/* Відновлення тактування після виходу з режиму STOP (C) */
void pm_restore_clocks_after_stop(void) {
    /* 1. Запуск зовнішнього кварцового резонатора HSE */
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY)) {
        /* Очікування прапорця апаратної стабілізації частоти кварцу */
    }

    /* 2. Запуск помножувача частоти PLL */
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) {
        /* Очікування фіксації фазового автопідстроювання PLL Lock */
    }

    /* 3. Перемикання системного джерела тактування SYSCLK на вихід PLL */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) {
        /* Перевірка успішного перемикання шини */
    }
}

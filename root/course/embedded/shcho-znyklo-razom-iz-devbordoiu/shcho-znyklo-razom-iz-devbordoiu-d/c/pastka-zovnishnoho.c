/* Наївна ініціалізація тактування з девборди (C) */
void SystemClock_Config_Naive(void) {
    /* Вмикаємо зовнішній кварц HSE */
    RCC->CR |= RCC_CR_HSEON;

    /* НЕБЕЗПЕКА: Нескінченний цикл очікування готовності кварцу! */
    while (!(RCC->CR & RCC_CR_HSERDY)) {
        /* Якщо кварцу немає, пошкоджено доріжку чи C_L хибний — 
           процесор зависає тут НАЗАВЖДИ ще до виклику main() */
    }

    /* Налаштування PLL та дільників шин... */
    RCC->PLLCFGR = (8 << RCC_PLLCFGR_PLLM_Pos) | (336 << RCC_PLLCFGR_PLLN_Pos) | (0 << RCC_PLLCFGR_PLLP_Pos);
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY));

    /* Перемикання системного такту на PLL */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL);
}

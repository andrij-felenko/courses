// ── Таймер-ЛІЧИЛЬНИК подій: тактується фронтами на ніжці (external clock) ──
static void counter_setup_external_clock(void)
{
    // Режим зовнішнього годинника: кожен фронт на каналі = один тик.
    // (на STM32 — ECM1/external clock mode, фільтрований вхід TI як джерело такту)
    TIM_CNT->SMCR &= ~TIM_SMCR_SMS_Msk;
    TIM_CNT->SMCR |=  TIM_SMCR_ECE;        // external clock enable
    TIM_CNT->ARR   =  0xFFFFFFFFu;         // 32-бітний таймер: широкий запас на події
    TIM_CNT->CR1  |=  TIM_CR1_CEN;
}

// ── Таймер-ВОРОТА: від кварцу відмірює рівне вікно T і видає TRGO ──
static void gate_setup_window(uint32_t window_ticks)
{
    // Лічить від системного такту; період = window_ticks; на update → TRGO.
    TIM_GATE->PSC = 0;
    TIM_GATE->ARR = window_ticks - 1;       // напр. 100 мс кварцу
    TIM_GATE->CR2 &= ~TIM_CR2_MMS_Msk;
    TIM_GATE->CR2 |=  TIM_CR2_MMS_1;        // MMS = 010: update → TRGO (кінець вікна)
    TIM_GATE->DIER |= TIM_DIER_UIE;         // переривання в кінці вікна — забрати число
}

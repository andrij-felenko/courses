// ── Розстановка пріоритетів. Число МЕНШЕ = терміновіше (Cortex-M). ───────
void setup_priorities(void)
{
    // Критичний таймер — пріоритет 0: найвищий, його ніхто не витісняє.
    NVIC_SetPriority(TIM_1ms_IRQn, 0);

    // Уся фонова периферія — свідомо НИЖЧЕ (числа більші),
    // щоб НІКОЛИ не заступити критичний таймер.
    NVIC_SetPriority(UART_IRQn,   5);
    NVIC_SetPriority(EXTI0_IRQn,  6);
    NVIC_SetPriority(DMA1_IRQn,   7);

    NVIC_EnableIRQ(TIM_1ms_IRQn);
    NVIC_EnableIRQ(UART_IRQn);
    // …
}

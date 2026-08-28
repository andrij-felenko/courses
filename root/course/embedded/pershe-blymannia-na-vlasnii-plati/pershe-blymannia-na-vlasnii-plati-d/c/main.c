/* Спрощена реалізація HAL_Delay з бібліотеки STM32Cube */
void HAL_Delay(uint32_t Delay) {
    uint32_t tickstart = HAL_GetTick();
    uint32_t wait = Delay;

    /* Додаємо один такт запасу, якщо лічильник на межі перемикання */
    if (wait < HAL_MAX_DELAY) {
        wait += (uint32_t)(uwTickFreq);
    }

    while ((HAL_GetTick() - tickstart) < wait) {
        /* Чекаємо, доки переривання SysTick збільшить глобальну змінну uwTick */
    }
}

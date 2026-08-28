/* STM32 HAL / CMSIS SysTick */
volatile uint32_t uwTick = 0;

void SysTick_Handler(void) {
    uwTick++;
}

uint32_t HAL_GetTick(void) {
    return uwTick;
}

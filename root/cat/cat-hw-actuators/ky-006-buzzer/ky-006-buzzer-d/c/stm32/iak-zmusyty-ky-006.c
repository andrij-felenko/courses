// ніжку описано як GPIO_Output: BUZ_GPIO_Port / BUZ_Pin
// HAL_Delay уміє лише мілісекунди, тож півперіод відміряємо грубим лічильником
static void delay_us(uint32_t us) {
    uint32_t ticks = us * (SystemCoreClock / 1000000U) / 4U;
    while (ticks--) __NOP();
}

void buzz_1khz(void)
{
    while (1) {
        // один цикл меандру 1000 Гц: 500 мкс вгорі + 500 мкс унизу
        HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_SET);
        delay_us(500);
        HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_RESET);
        delay_us(500);
    }
}

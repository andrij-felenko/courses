// TIM3_CH1 на ніжці S; лічильник із кроком 1 мкс,
// захоплення по ОБОХ перепадах (CubeMX: Input Capture, Both Edges)
extern TIM_HandleTypeDef htim3;

static uint32_t prev;             // мітка попереднього перепаду, мкс
static uint16_t addr, cmd;

void ir_start(void)
{
    HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_1);   // старт приймання
}

// перепад на виводі S: рахуємо, скільки тривав попередній рівень
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance != TIM3) return;

    uint32_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    uint32_t dt  = (now - prev) & 0xFFFF;   // лічильник 16-бітний, різниця сама «обертається»
    prev = now;

    // nec_feed() — власний автомат протоколу: годуємо довжинами, він збирає кадр
    if (nec_feed(dt, &addr, &cmd))
        printf("протокол: NEC  команда: 0x%02X\r\n", cmd);
}

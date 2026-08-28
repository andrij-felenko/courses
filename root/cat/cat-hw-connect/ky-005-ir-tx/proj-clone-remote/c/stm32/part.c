/* TIM3: лічильник на 1 МГц (1 тик = 1 мкс), CH1 — захоплення на ОБОХ фронтах.
   Вхід CH1 — вихід ІЧ-приймача. nec_decode() — свій десяток рядків: біт = 1,
   якщо пауза після імпульсу ≈1690 мкс, і 0, якщо ≈560 мкс. */
extern TIM_HandleTypeDef htim3;

#define MAX_GAPS 140
static uint16_t gap[MAX_GAPS];        // тривалості імпульсів і пауз, мкс
static volatile uint16_t n_gaps;
static uint16_t prev;

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    uint16_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    if (n_gaps < MAX_GAPS) gap[n_gaps++] = now - prev;   // різниця й є тривалість
    prev = now;
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM3_Init(); MX_USART2_UART_Init();
    HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_1);          // почати приймання
    printf("Тисни кнопки пульта...\r\n");

    while (1) {
        HAL_Delay(100);                   // пауза довша за міжкадрову — кадр завершився
        if (n_gaps > 66) {                // NEC: преамбула + 32 біти
            uint8_t addr, cmd;
            if (nec_decode(gap, n_gaps, &addr, &cmd))
                printf("NEC address=0x%02X command=0x%02X\r\n", addr, cmd);
        }
        n_gaps = 0;                       // готові ловити наступну кнопку
    }
}

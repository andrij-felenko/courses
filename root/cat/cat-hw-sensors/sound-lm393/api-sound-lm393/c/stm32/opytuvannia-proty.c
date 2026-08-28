#define SOUND_PORT GPIOA
#define SOUND_PIN  GPIO_PIN_0            // вивід DO давача
// у MX_GPIO_Init: Mode = GPIO_MODE_INPUT, Pull = GPIO_NOPULL
// (підтяжка вже стоїть на платі давача)

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();               // printf перенаправлено в UART

    GPIO_PinState prev = GPIO_PIN_SET;   // спокій = 1
    while (1) {
        GPIO_PinState now = HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN);
        if (prev == GPIO_PIN_SET && now == GPIO_PIN_RESET) {   // фронт «1→0»
            printf("звук!\r\n");
        }
        prev = now;
        // жодного HAL_Delay: цикл летить, проміжок між читаннями — мікросекунди
    }
}

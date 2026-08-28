#define SOUND_PORT GPIOA
#define SOUND_PIN  GPIO_PIN_0
#define WINDOW     150u                  // вікно дебаунсу, мс

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

    uint32_t lastHit = 0;                // час останньої ЗАРАХОВАНОЇ події
    uint32_t count   = 0;
    GPIO_PinState prev = GPIO_PIN_SET;

    while (1) {
        GPIO_PinState now = HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN);
        uint32_t t = HAL_GetTick();      // мілісекунди від старту, як millis()

        // спадний фронт І минуло вікно від попередньої події
        if (prev == GPIO_PIN_SET && now == GPIO_PIN_RESET && t - lastHit > WINDOW) {
            lastHit = t;
            printf("плеск #%lu\r\n", (unsigned long)++count);
        }
        prev = now;
        // програма НЕ спить: жодного HAL_Delay у циклі
    }
}

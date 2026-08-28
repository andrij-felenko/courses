#define SOUND_PIN GPIO_PIN_0
#define WINDOW    150u

volatile uint32_t lastHit = 0;
volatile uint32_t count   = 0;
volatile bool     ready   = false;

void HAL_GPIO_EXTI_Callback(uint16_t pin) {   // обробник
    if (pin != SOUND_PIN) return;
    uint32_t t = HAL_GetTick();     // тік читати в ISR можна, HAL_Delay — ні
    if (t - lastHit > WINDOW) {     // дебаунс прямо в перериванні
        lastHit = t;
        count++;
        ready = true;
    }
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();
    while (1) {
        if (ready) {
            ready = false;
            printf("плеск #%lu\r\n", (unsigned long)count);   // друк поза ISR
        }
    }
}

#define SOUND_PORT GPIOA
#define SOUND_PIN  GPIO_PIN_0

volatile bool     hit    = false;              // прапорець «була подія»
volatile uint32_t hit_at = 0;                  // коли саме, мс (для дебаунсу)

// у MX_GPIO_Init: Mode = GPIO_MODE_IT_FALLING, Pull = GPIO_NOPULL, далі
// HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0) і HAL_NVIC_EnableIRQ(EXTI0_IRQn) —
// без увімкненого вектора переривання не дійде
void HAL_GPIO_EXTI_Callback(uint16_t pin) {    // спільний обробник усіх ліній EXTI
    if (pin != SOUND_PIN) return;
    hit    = true;
    hit_at = HAL_GetTick();
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();
    while (1) {
        if (hit) {                             // головний цикл збирає врожай
            hit = false;
            printf("звук (по перериванню)!\r\n");
        }
        // тут можна робити будь-що важке — EXTI не проґавить фронт
    }
}

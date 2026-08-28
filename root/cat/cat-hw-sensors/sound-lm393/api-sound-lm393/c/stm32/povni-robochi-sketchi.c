/* Звуковий давач на LM393 → STM32 (HAL, приклад під F1/F4).
   DO давача на PA0 (лінія EXTI0), світлодіод плати на PA5.
   Спокій = 1, звук = короткий 0. Дебаунс неблокуючий, у перериванні. */

#define SOUND_PORT GPIOA
#define SOUND_PIN  GPIO_PIN_0             // DO на ногу з лінією EXTI0
#define LED_PORT   GPIOA
#define LED_PIN    GPIO_PIN_5             // світлодіод плати
#define WINDOW     150u                   // вікно дебаунсу, мс

volatile uint32_t lastHit = 0;
volatile uint32_t count   = 0;
volatile bool     ready   = false;

/* MX_GPIO_Init: PA0 — GPIO_MODE_IT_FALLING / GPIO_NOPULL (підтяжка на платі),
   PA5 — GPIO_MODE_OUTPUT_PP; далі HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0)
   і HAL_NVIC_EnableIRQ(EXTI0_IRQn). */

void HAL_GPIO_EXTI_Callback(uint16_t pin) {   // обробник: лише відсів і позначка
    if (pin != SOUND_PIN) return;
    uint32_t t = HAL_GetTick();     // тік у ISR читати можна, HAL_Delay — ні
    if (t - lastHit > WINDOW) {     // ігноруємо торохтіння того ж плеску
        lastHit = t;
        count++;
        ready = true;
    }
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();
    printf("готово. плесніть у долоні.\r\n");

    while (1) {
        if (ready) {                          // головний цикл збирає врожай
            ready = false;
            HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
            printf("плеск #%lu\r\n", (unsigned long)count);
            HAL_Delay(30);                    // коротке блимання
            HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
        }
        // сюди можна вставити будь-яку іншу роботу — EXTI не проґавить звук
    }
}

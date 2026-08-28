#include "main.h"
#include <stdio.h>

#define SHOCK_PORT   GPIOA
#define SHOCK_PIN    GPIO_PIN_0
#define SHOCK_IRQ    EXTI0_IRQn
#define WINDOW_MS    100u           // вікно вимірювання сили
#define STRONG_HITS  12u            // поріг «сильний струс» (імпульсів за вікно)

volatile uint32_t g_hits = 0;       // фронти в поточному вікні (нарощує ISR)

void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(SHOCK_PIN); }

void HAL_GPIO_EXTI_Callback(uint16_t pin) {      // максимально коротка ISR
    if (pin == SHOCK_PIN) g_hits++;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef g = {0};
    g.Pin = SHOCK_PIN;  g.Mode = GPIO_MODE_INPUT;  g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(SHOCK_PORT, &g);
    HAL_Delay(50);

    GPIO_PinState idle = HAL_GPIO_ReadPin(SHOCK_PORT, SHOCK_PIN);
    g.Mode = (idle == GPIO_PIN_SET) ? GPIO_MODE_IT_FALLING : GPIO_MODE_IT_RISING;
    HAL_GPIO_Init(SHOCK_PORT, &g);
    HAL_NVIC_SetPriority(SHOCK_IRQ, 5, 0);
    HAL_NVIC_EnableIRQ(SHOCK_IRQ);

    uint32_t windowStart = HAL_GetTick();
    while (1) {
        if (HAL_GetTick() - windowStart < WINDOW_MS) continue;
        windowStart += WINDOW_MS;

        // Забрати й обнулити лічильник вікна атомарно.
        __disable_irq();
        uint32_t hits = g_hits;
        g_hits = 0;
        __enable_irq();

        if (hits == 0) continue;                 // тиша — нічого не друкуємо
        printf("%s струс: %lu імпульсів\r\n",
               hits >= STRONG_HITS ? "СИЛЬНИЙ" : "легкий", (unsigned long)hits);
    }
}

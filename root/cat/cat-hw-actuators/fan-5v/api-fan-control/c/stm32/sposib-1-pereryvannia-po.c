// STM32 HAL: підрахунок обертів через зовнішнє переривання EXTI на виводі PB7
#include "stm32f4xx_hal.h"
#include <stdio.h>

#define TACH_PIN   GPIO_PIN_7
#define TACH_PORT  GPIOB

volatile uint32_t tachEdges = 0;             // лічильник фронтів — його чіпає ISR

void EXTI9_5_IRQHandler(void) {              // лінії EXTI5…9 сидять на одному векторі
    HAL_GPIO_EXTI_IRQHandler(TACH_PIN);
}

void HAL_GPIO_EXTI_Callback(uint16_t pin) {  // спільний колбек усіх ліній EXTI
    if (pin == TACH_PIN) tachEdges++;        // тільки інкремент
}

void tach_begin(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = TACH_PIN;
    g.Mode = GPIO_MODE_IT_RISING;            // переривання на висхідному фронті
    g.Pull = GPIO_PULLUP;                    // підтяжка — тахо це відкритий колектор
    HAL_GPIO_Init(TACH_PORT, &g);
    HAL_NVIC_SetPriority(EXTI9_5_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    tach_begin();

    uint32_t lastMs = 0;
    while (1) {
        uint32_t now = HAL_GetTick();
        if (now - lastMs >= 1000) {           // раз на секунду
            lastMs = now;
            __disable_irq();                  // атомарно зняти й скинути
            uint32_t edges = tachEdges;
            tachEdges = 0;
            __enable_irq();

            uint32_t rpm = (edges / 2) * 60;  // ÷2 ×60
            printf("TACH: %lu імп/с  ->  %lu об/хв\r\n",
                   (unsigned long)edges, (unsigned long)rpm);
        }
    }
}

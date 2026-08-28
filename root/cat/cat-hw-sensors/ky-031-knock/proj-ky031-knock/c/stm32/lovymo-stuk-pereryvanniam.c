#include "main.h"
#include <stdio.h>                    // printf перенаправлено на UART

#define LOCKOUT 60u                   // глухе вікно після стуку, мс

volatile uint8_t knockFlag = 0;       // ставить обробник, скидає main

/* HAL сам кличе цей колбек із обробника EXTI — тримаємо його КРИХІТНИМ */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == GPIO_PIN_0) knockFlag = 1;    // єдина дія — звести прапорець
}

/* у stm32xxxx_it.c: вектор EXTI0 віддає керування в HAL */
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;              // PA0 — вивід S
    g.Mode = GPIO_MODE_IT_FALLING;    // вхід із перериванням на фронті спаду
    g.Pull = GPIO_PULLUP;             // внутрішня підтяжка: спокій = 1
    HAL_GPIO_Init(GPIOA, &g);
    g.Pin   = GPIO_PIN_13;            // PC13 — світлодіод
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    uint32_t lastKnock = 0, count = 0;
    while (1) {
        if (knockFlag) {                        // обробник щось зафіксував
            knockFlag = 0;                      // одразу скидаємо
            uint32_t now = HAL_GetTick();       // мілісекунди від старту
            if (now - lastKnock > LOCKOUT) {    // поза вікном — правдивий стук
                lastKnock = now;
                count++;
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
                printf("стук #%lu\r\n", (unsigned long)count);
            }
            // якщо всередині вікна — це відскок пружини, мовчимо
        }
        if (HAL_GetTick() - lastKnock > 30)     // гасимо світлодіод
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    }
}

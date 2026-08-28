#include "stm32f4xx_hal.h"
#include <stdio.h>

#define TOUCH_PORT  GPIOA                 // будь-який пін годиться: у STM32
#define TOUCH_PIN   GPIO_PIN_0            // переривання дає лінія EXTI

volatile uint32_t touchCount = 0;         // спільні з ISR → обов'язково volatile
volatile bool     touchFlag  = false;

static void touch_exti_init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin  = TOUCH_PIN;
    gpio.Mode = GPIO_MODE_IT_RISING;      // передній фронт = активація для акт.-у-1
    gpio.Pull = GPIO_NOPULL;              // двотактний вихід → без підтяжки
    HAL_GPIO_Init(TOUCH_PORT, &gpio);

    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);       // дозволяємо вектор у контролері переривань
}

void EXTI0_IRQHandler(void) {             // вектор: HAL зніме прапорець і покличе колбек
    HAL_GPIO_EXTI_IRQHandler(TOUCH_PIN);
}

// Обробник: максимально короткий, без printf/HAL_Delay усередині!
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == TOUCH_PIN) { touchCount++; touchFlag = true; }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    touch_exti_init();

    while (1) {
        if (touchFlag) {                  // прапорець підняв обробник
            touchFlag = false;            // скинули й обробляємо в спокійному циклі
            printf("дотиків: %lu\r\n", (unsigned long)touchCount);
        }
        // процесор тут вільний: __WFI(), інша логіка — реакція прийде сама
    }
}

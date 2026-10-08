/* C (STM32 HAL) — Обробка переривання цифрового давача Холла */
#include "stm32f4xx_hal.h"

volatile uint32_t pulse_count = 0;

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == HALL_SENSOR_PIN) {
        /* Фіксація спадаючого фронту при спрацьовуванні давача */
        pulse_count++;
    }
}

void System_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    /* Налаштування виводу PA0 на вхід переривання по спадаючому фронту */
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    /* Дозвіл та встановлення пріоритету EXTI0 */
    HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

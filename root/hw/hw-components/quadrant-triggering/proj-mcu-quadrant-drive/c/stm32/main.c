/* STM32 HAL: Негативний затворний імпульс (активний LOW) з пачкою імпульсів */
#include "stm32f4xx_hal.h"

#define TRIAC_PORT            GPIOB
#define TRIAC_PIN             GPIO_PIN_0
#define ZERO_CROSS_PIN        GPIO_PIN_1

#define PULSE_TRAIN_COUNT     20     /* 20 імпульсів у пачці */
#define PULSE_HIGH_US         10     /* Тривалість активного імпульсу 10 мкс */
#define PULSE_LOW_US          30     /* Пауза між імпульсами 30 мкс */

extern TIM_HandleTypeDef htim2;
volatile uint32_t phase_delay_ticks = 5000; /* Затримка фази (мкс) */

/* Обробник зовнішнього переривання переходу через нуль */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == ZERO_CROSS_PIN) {
        /* Перезапуск таймера фазової затримки */
        __HAL_TIM_SET_AUTORELOAD(&htim2, phase_delay_ticks);
        __HAL_TIM_SET_COUNTER(&htim2, 0);
        HAL_TIM_Base_Start_IT(&htim2);
    }
}

/* Обробник спрацьовування таймера кута відсікання */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        HAL_TIM_Base_Stop_IT(&htim2);
        
        /* Генерація пачки від'ємних імпульсів (активний нуль на затворі) */
        for (int i = 0; i < PULSE_TRAIN_COUNT; i++) {
            /* Стан 0: струм витікає із затвора в пін GND МК (квадранти II/III) */
            HAL_GPIO_WritePin(TRIAC_PORT, TRIAC_PIN, GPIO_PIN_RESET);
            delay_us(PULSE_HIGH_US);
            
            /* Стан 1: затвор з'єднано з VCC (MT1), струм припинено */
            HAL_GPIO_WritePin(TRIAC_PORT, TRIAC_PIN, GPIO_PIN_SET);
            delay_us(PULSE_LOW_US);
        }
    }
}

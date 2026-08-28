#include "stm32f4xx_hal.h"

TIM_HandleTypeDef htim3;                       // TIM3_CH1 виведений на PA6

void ir_begin(void) {                          // несуча — канал ШІМ таймера
    __HAL_RCC_TIM3_CLK_ENABLE();
    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 0;                          // таймер тактується 84 МГц
    htim3.Init.Period = 84000000 / 38000 - 1;          // ≈ 2210 → 38 кГц
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    HAL_TIM_PWM_Init(&htim3);

    TIM_OC_InitTypeDef oc = {0};
    oc.OCMode = TIM_OCMODE_PWM1;
    oc.Pulse = (htim3.Init.Period + 1) / 3;            // ≈ 1/3 — як світить пульт
    HAL_TIM_PWM_ConfigChannel(&htim3, &oc, TIM_CHANNEL_1);
}

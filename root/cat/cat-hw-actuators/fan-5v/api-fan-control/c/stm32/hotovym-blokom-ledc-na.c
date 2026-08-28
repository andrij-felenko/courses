// Те саме на STM32 HAL: TIM3, канал 1 у режимі PWM, 25 кГц
// Тактова таймера (APB1 timer clock) 84 МГц → 84e6 / 25e3 = 3360 кроків на період
#include "stm32f4xx_hal.h"

#define PWM_TOP  3359                     // 84 МГц / 25 кГц − 1

TIM_HandleTypeDef htim3;

static void fan_set_speed(uint8_t percent) {          // 0…100 %
    if (percent > 100) percent = 100;
    uint32_t duty = (uint32_t)percent * PWM_TOP / 100;
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
}

void fan_pwm_begin(void) {
    __HAL_RCC_TIM3_CLK_ENABLE();
    // вивід у режим альтернативної функції TIM3_CH1 налаштовує HAL_TIM_PWM_MspInit()

    htim3.Instance           = TIM3;
    htim3.Init.Prescaler     = 0;                     // без дільника — повна роздільність
    htim3.Init.CounterMode   = TIM_COUNTERMODE_UP;
    htim3.Init.Period        = PWM_TOP;               // верх лічильника задає частоту
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_PWM_Init(&htim3);

    TIM_OC_InitTypeDef oc = {0};
    oc.OCMode     = TIM_OCMODE_PWM1;                  // не-інверсний ШІМ
    oc.Pulse      = 0;                                // старт: вентилятор стоїть
    oc.OCPolarity = TIM_OCPOLARITY_HIGH;
    HAL_TIM_PWM_ConfigChannel(&htim3, &oc, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    fan_pwm_begin();
    fan_set_speed(50);                                // старт на 50 %

    while (1) {   // повільний «вдих-видих» швидкістю
        for (int p = 20; p <= 100; p += 5) { fan_set_speed(p); HAL_Delay(200); }
        for (int p = 100; p >= 20; p -= 5) { fan_set_speed(p); HAL_Delay(200); }
    }
}

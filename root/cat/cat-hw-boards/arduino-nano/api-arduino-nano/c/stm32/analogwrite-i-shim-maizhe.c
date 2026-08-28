#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim2;   // TIM2_CH1 на PA0, ARR = 255 (виставлено в CubeMX)

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM2_Init();
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);

    while (1) {
        // плавне «дихання»: яскравість вгору й вниз; CCR — це і є duty
        for (int d = 0; d <= 255; d++) {
            __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, d);
            HAL_Delay(5);
        }
        for (int d = 255; d >= 0; d--) {
            __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, d);
            HAL_Delay(5);
        }
    }
}

// STM32 HAL. Період відмірює TIM2 у перериванні — процесор на крок не впливає.
#include "stm32f4xx_hal.h"

volatile bool tick = false;
extern TIM_HandleTypeDef htim2;             // CubeMX: TIM2, дільник зведено до ліку 1 МГц

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef* htim) {
    if (htim->Instance == TIM2) tick = true;   // лише прапорець — коротко й без блокувань
}

void setup_sampler(uint32_t fs_hz) {
    __HAL_TIM_SET_AUTORELOAD(&htim2, (1000000U / fs_hz) - 1);  // період = 1/fs у мкс
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    HAL_TIM_Base_Start_IT(&htim2);
}

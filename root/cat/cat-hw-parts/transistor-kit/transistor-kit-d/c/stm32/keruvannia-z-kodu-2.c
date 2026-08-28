/* TIM3 у CubeMX: канал 1 у режимі PWM Generation, Period (ARR) = 255,
   передільник підібрано під частоту ~1 кГц. Вивід — TIM3_CH1. */
extern TIM_HandleTypeDef htim3;

void Lamp_Fade(void) {
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);

    while (1) {
        for (int duty = 0; duty <= 255; duty++) {          // плавне розгоряння
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);  // 0 = темно, 255 = повний
            HAL_Delay(8);
        }
        for (int duty = 255; duty >= 0; duty--) {          // плавне згасання
            __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
            HAL_Delay(8);
        }
    }
}

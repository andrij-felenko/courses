extern TIM_HandleTypeDef htim2;  // 32-біт, прескалер під 1 такт = 1 мкс,
                                 // запущений раз через HAL_TIM_Base_Start(&htim2)

float measure_capacitance(float R_ohms) {
    static uint32_t discharge_us = 200000;   // щедрий старт на перший цикл

    GPIO_InitTypeDef g = { .Pin = DRIVE_PIN, .Mode = GPIO_MODE_OUTPUT_PP,
                           .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW };
    HAL_GPIO_Init(DRIVE_PORT, &g);

    HAL_GPIO_WritePin(DRIVE_PORT, DRIVE_PIN, GPIO_PIN_RESET);  // 1. розряд крізь R
    uint32_t d0 = __HAL_TIM_GET_COUNTER(&htim2);
    while (__HAL_TIM_GET_COUNTER(&htim2) - d0 < discharge_us) { /* поки не сяде */ }

    uint32_t t0 = __HAL_TIM_GET_COUNTER(&htim2);
    HAL_GPIO_WritePin(DRIVE_PORT, DRIVE_PIN, GPIO_PIN_SET);    // 2. старт заряду

    while (HAL_GPIO_ReadPin(SENSE_PORT, SENSE_PIN) == GPIO_PIN_RESET) { } // 3. поріг
    uint32_t t_us = __HAL_TIM_GET_COUNTER(&htim2) - t0;        //    ≈ 0.69·τ

    discharge_us = 8 * t_us;                 // наступний розряд: 8·0.69τ ≈ 5.5τ ≥ 5τ
    return (t_us * 1e-6f) / (0.693f * R_ohms); // 4. ділимо на k·R → фаради
}

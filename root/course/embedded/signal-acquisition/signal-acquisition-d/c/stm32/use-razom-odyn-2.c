// Те саме на HAL: канал уже вибрано в CubeMX, перше перетворення — холосте.
// N обираємо з потрібної чистоти: треба σ/√N ≤ ціль  →  N ≥ (σ/ціль)².
static uint32_t read_clean(ADC_HandleTypeDef* hadc, int n) {
    uint32_t acc = 0;                         // 32 біти: 256×4095 не переповнить
    for (int i = -1; i < n; ++i) {            // i = −1 — холостий (гасить crosstalk-хвіст)
        HAL_ADC_Start(hadc);
        HAL_ADC_PollForConversion(hadc, 10);  // стеля 10 мс — з великим запасом
        uint32_t v = HAL_ADC_GetValue(hadc);
        if (i >= 0) acc += v;
    }
    HAL_ADC_Stop(hadc);
    return acc / (uint32_t)n;                 // середнє, 0..4095
}

// Припускаємо: TIM2 налаштований у CubeMX так, щоб тікати раз на 1 мкс.
// Для цього Prescaler = (частота_шини_таймера в МГц) − 1.
// Напр. якщо TIM2 живиться від 72 МГц → Prescaler = 71,
// тоді лічильник збільшується на 1 кожну мікросекунду.

static inline uint32_t micros(void) {
    return __HAL_TIM_GET_COUNTER(&htim2);   // лічильник = мікросекунди
}

// Затримка в мікросекундах через той самий таймер.
static void delay_us(uint32_t us) {
    uint32_t start = __HAL_TIM_GET_COUNTER(&htim2);
    while ((uint32_t)(__HAL_TIM_GET_COUNTER(&htim2) - start) < us) { }
}

#define SAMPLE_MS  20               // період опитування: 20 мс = 50 Гц

static uint32_t g_lastSample = 0;

while (1) {
    uint32_t now = HAL_GetTick();               // мілісекунди від старту
    if (now - g_lastSample >= SAMPLE_MS) {
        g_lastSample += SAMPLE_MS;              // НЕ '= now' — так період не «повзе»
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 10);
        process(HAL_ADC_GetValue(&hadc1));      // уся обробка — тут
        HAL_ADC_Stop(&hadc1);
    }
    // ...цикл вільний робити будь-що інше...
}

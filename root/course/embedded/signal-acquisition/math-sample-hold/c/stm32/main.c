#include "stm32f4xx_hal.h"           // STM32 HAL, регулярний канал, опитування

static uint32_t adc_once(ADC_HandleTypeDef *h) {
    HAL_ADC_Start(h);
    HAL_ADC_PollForConversion(h, 10);        // 10 мс — стеля очікування
    uint32_t v = HAL_ADC_GetValue(h);
    HAL_ADC_Stop(h);
    return v;
}

int read_clean(ADC_HandleTypeDef *h, uint32_t channel, int n) {
    ADC_ChannelConfTypeDef s = {0};
    s.Channel = channel;
    s.Rank = 1;
    s.SamplingTime = ADC_SAMPLETIME_84CYCLES;  // це і є t_acq — купуємо кілька τ
    HAL_ADC_ConfigChannel(h, &s);              // саме тут відбувається перемикання

    adc_once(h);                             // холостий: гасить хвіст старого каналу
    uint32_t acc = 0;                        // 32 біти: 16×4095 не переповнить
    for (int i = 0; i < n; ++i)              // усереднення: шум ↓ як √n
        acc += adc_once(h);
    return (int)(acc / n);                   // середнє, 0..4095
}

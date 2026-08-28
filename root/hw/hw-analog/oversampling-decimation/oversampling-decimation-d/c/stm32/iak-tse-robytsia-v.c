#include "stm32f4xx_hal.h"

// Просте усереднення 16 знімків — повертає те саме 12-бітне число, лише чистіше.
// Канал уже налаштовано (одиничне перетворення), hadc — ADC_HandleTypeDef.
uint16_t read_avg16(ADC_HandleTypeDef *hadc) {
    uint32_t acc = 0;
    for (int i = 0; i < 16; i++) {
        HAL_ADC_Start(hadc);
        HAL_ADC_PollForConversion(hadc, 10);  // 16 знімків того самого входу
        acc += HAL_ADC_GetValue(hadc);
    }
    HAL_ADC_Stop(hadc);
    return (uint16_t)(acc / 16);    // середнє — у тому самому масштабі 0..4095
}

#include "stm32f4xx_hal.h"
#include <stdio.h>

#define WINDOW_MS  50                    // вікно вимірювання, мс

extern ADC_HandleTypeDef hadc1;          // AO — на канал ADC1 (напр. PA0 = IN0)

static uint16_t adc_sample(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 1);   // одне перетворення, чекати до 1 мс
    uint16_t v = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return v;
}

int measure_peak_to_peak(void) {
    uint32_t t0 = HAL_GetTick();
    int hi = 0, lo = 4095;               // межі 12-бітного АЦП STM32
    while (HAL_GetTick() - t0 < WINDOW_MS) {
        int v = adc_sample();            // миттєва точка хвилі
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;                      // РОЗМАХ: тиша ≈ мало, гучно ≈ багато
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();                      // канал, час вибірки — з генератора CubeMX
    while (1) printf("%d\r\n", measure_peak_to_peak());
}

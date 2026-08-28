#include "stm32f4xx_hal.h"
#include <math.h>
#include <stdio.h>

// adc_sample() і WINDOW_MS — з прикладу розмаху вище

float measure_rms(void) {
    // --- прохід 1: середнє (робоча точка) за вікно ---
    uint32_t t0 = HAL_GetTick();
    uint32_t sum = 0;
    int      n = 0;
    while (HAL_GetTick() - t0 < WINDOW_MS) {
        sum += adc_sample();
        n++;
    }
    float mean = (float)sum / n;

    // --- прохід 2: сума квадратів відхилень від середнього ---
    t0 = HAL_GetTick();
    float sum_sq = 0;
    int   n2 = 0;
    while (HAL_GetTick() - t0 < WINDOW_MS) {
        float d = adc_sample() - mean;
        sum_sq += d * d;
        n2++;
    }
    return sqrtf(sum_sq / n2);        // RMS-відхилення в одиницях АЦП
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();
    while (1) printf("%.1f\r\n", measure_rms());
}

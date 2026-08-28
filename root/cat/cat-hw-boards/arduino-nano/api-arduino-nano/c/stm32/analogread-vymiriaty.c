#include "stm32f4xx_hal.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;   // канал і час вибірки виставлено в CubeMX

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_ADC1_Init(); MX_USART2_UART_Init();

    while (1) {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            uint32_t raw = HAL_ADC_GetValue(&hadc1);   // 0..4095, 12 бітів
            float volts = raw * 3.3f / 4095.0f;        // назад у вольти
            printf("%lu  ->  %.3f В\r\n", (unsigned long)raw, volts);
        }
        HAL_ADC_Stop(&hadc1);
        HAL_Delay(200);
    }
}

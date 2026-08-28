// STM32 HAL: той самий конвеєр, АЦП опитуємо поллінгом
#include "stm32f4xx_hal.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define ADC_MAX   4095.0f            // 12-біт АЦП: повна шкала (2^12 − 1)
#define R_FIXED   10000.0f           // сталий резистор на модулі, Ом
#define R25       10000.0f           // опір термістора за 25 °C, Ом
#define BETA      3950.0f            // B-параметр термістора, K
#define T25_K     298.15f            // 25 °C у кельвінах

extern ADC_HandleTypeDef  hadc1;     // канал під сигнал S налаштований у CubeMX
extern UART_HandleTypeDef huart2;    // вивід замість Serial

static uint16_t adc_read(void) {     // один відлік із каналу
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
    uint16_t raw = (uint16_t)HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return raw;
}

// відлік АЦП → опір термістора (термістор у ВЕРХНЬОМУ плечі)
static float raw_to_resistance(uint16_t raw) {
    float ratio = (float)raw / ADC_MAX;          // U_S / Vcc, у межах 0..1
    return R_FIXED * (1.0f / ratio - 1.0f);      // R_ntc = R_fixed·(1/ratio − 1)
}

// опір термістора → температура, °C (B-параметр)
static float resistance_to_temp_c(float r_ntc) {
    float invT = 1.0f / T25_K + logf(r_ntc / R25) / BETA;
    return 1.0f / invT - 273.15f;                // K → °C
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART2_UART_Init();

    char line[24];
    while (1) {
        float tempC = resistance_to_temp_c(raw_to_resistance(adc_read()));
        int t10 = (int)lroundf(tempC * 10.0f);   // друкуємо цілими: десяті окремо,
        int n = snprintf(line, sizeof line, "%d.%d C\r\n",
                         t10 / 10, abs(t10 % 10));  // щоб не тягнути float у printf
        HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
        HAL_Delay(500);
    }
}

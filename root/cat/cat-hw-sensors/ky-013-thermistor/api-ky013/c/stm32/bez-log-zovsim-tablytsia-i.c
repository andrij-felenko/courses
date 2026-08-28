// На STM32 flash теж відображена в загальний адресний простір: const-масив
// лежить у flash і читається звичайним індексуванням. Саме тут, на Cortex-M0/M3
// без FPU, ціла таблиця й виграє в logf найбільше.
#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <stdlib.h>

extern ADC_HandleTypeDef  hadc1;
extern UART_HandleTypeDef huart2;

typedef struct { int16_t adc; int16_t t10; } Point;

// «відлік АЦП → температура×10 (десяті °C)», шкала 12-бітна (0…4095).
// Термістор УНИЗУ (між S і −): гарячіше → напруга на S нижча → відлік менший.
static const Point TABLE[] = {
    {3495, -100}, {3338,  -50}, {3154,    0}, {2954,   50},
    {2738,  100}, {2510,  150}, {2278,  200}, {2050,  250},
    {1825,  300}, {1613,  350}, {1417,  400}, {1241,  450},
};
#define N  (sizeof(TABLE) / sizeof(TABLE[0]))

// відлік → температура×10, лінійна інтерполяція по таблиці (без float!)
static int16_t lookup_t10(int16_t raw) {
    if (raw >= TABLE[0].adc)     return TABLE[0].t10;      // за краєм — обрізаємо
    if (raw <= TABLE[N - 1].adc) return TABLE[N - 1].t10;

    for (size_t i = 0; i < N - 1; i++) {
        int16_t aHi = TABLE[i].adc;          // більший відлік
        int16_t aLo = TABLE[i + 1].adc;      // менший відлік
        if (raw <= aHi && raw >= aLo) {
            int16_t tHi = TABLE[i].t10, tLo = TABLE[i + 1].t10;
            // t = tHi + (tLo − tHi)·(aHi − raw)/(aHi − aLo), уся арифметика ціла
            int32_t num = (int32_t)(tLo - tHi) * (aHi - raw);
            return tHi + (int16_t)(num / (aHi - aLo));
        }
    }
    return TABLE[N - 1].t10;                 // сюди не дійде, для повноти
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_USART2_UART_Init();

    char line[24];
    while (1) {
        int16_t t10 = lookup_t10((int16_t)adc_read());
        int n = snprintf(line, sizeof line, "%d.%d C\r\n",
                         t10 / 10, abs(t10 % 10));
        HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
        HAL_Delay(500);
    }
}

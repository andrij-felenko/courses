#include "stm32f4xx_hal.h"

#define LOAD_PORT GPIOB
#define LOAD_PIN  GPIO_PIN_5    // MOSFET резистора-«гирі»
#define TRIG_PORT GPIOB
#define TRIG_PIN  GPIO_PIN_6    // зовнішній запуск осцилографа

// HAL_Delay() міряє мілісекундами, а нам треба 500 мкс — беремо лічильник тактів ядра.
// DWT вмикають один раз при старті:
//   CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
static void delay_us(uint32_t us) {
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = us * (HAL_RCC_GetHCLKFreq() / 1000000U);
    while ((DWT->CYCCNT - start) < ticks) { }
}

void load_step(void) {
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);     // армуємо запуск осцилографа
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_SET);     // різко даємо повне навантаження
    delay_us(500);                                            // поки контур відпрацює провал і дзвін
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_RESET);   // знімаємо навантаження
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);
}

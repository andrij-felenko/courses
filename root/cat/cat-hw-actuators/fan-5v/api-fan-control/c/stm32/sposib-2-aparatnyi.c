// STM32 HAL: PCNT-а тут немає, зате є таймер у режимі зовнішнього тактування —
// кожен фронт на вході TI1 крутить лічильник TIM2. Процесор лише знімає результат.
#include "stm32f4xx_hal.h"
#include <stdio.h>

TIM_HandleTypeDef htim2;                     // TIM2_CH1 = PA0, сюди заходить TACH

void tach_counter_begin(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin       = GPIO_PIN_0;
    g.Mode      = GPIO_MODE_AF_PP;
    g.Pull      = GPIO_PULLUP;               // підтяжка — сигнал OC
    g.Alternate = GPIO_AF1_TIM2;             // PA0 → вхід TIM2_CH1
    HAL_GPIO_Init(GPIOA, &g);
    __HAL_RCC_TIM2_CLK_ENABLE();

    htim2.Instance         = TIM2;
    htim2.Init.Prescaler   = 0;
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period      = 0xFFFFFFFF;     // TIM2 32-бітний — стелі тут не досягти
    HAL_TIM_Base_Init(&htim2);

    TIM_ClockConfigTypeDef clk = {0};
    clk.ClockSource    = TIM_CLOCKSOURCE_TI1;        // тактувати лічильник самим входом
    clk.ClockPolarity  = TIM_CLOCKPOLARITY_RISING;   // рахувати висхідні фронти
    clk.ClockPrescaler = TIM_CLOCKPRESCALER_DIV1;
    clk.ClockFilter    = 8;                          // цифровий фільтр — аналог glitch-фільтра
    HAL_TIM_ConfigClockSource(&htim2, &clk);

    HAL_TIM_Base_Start(&htim2);              // пуск: далі рахує саме залізо
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    tach_counter_begin();

    uint32_t lastMs = 0;
    while (1) {
        uint32_t now = HAL_GetTick();
        if (now - lastMs >= 1000) {                        // вимірюємо рівно за секунду
            lastMs = now;
            uint32_t count = __HAL_TIM_GET_COUNTER(&htim2);
            __HAL_TIM_SET_COUNTER(&htim2, 0);              // скид на новий інтервал

            uint32_t rpm = (count / 2) * 60;               // ÷2 ×60
            printf("TACH: %lu імп/с  ->  %lu об/хв\r\n",
                   (unsigned long)count, (unsigned long)rpm);
        }
    }
}

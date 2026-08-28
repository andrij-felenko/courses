#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"

void tim1_complementary_pwm_init(uint32_t timer_clk_hz, uint32_t pwm_freq_hz, uint32_t dead_time_ns) {
    // 1. Увімкнення тактування портів GPIO та таймера TIM1
    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);

    // 2. Конфігурація виводів: PA8 (CH1, High-Side), PB13 (CH1N, Low-Side)
    LL_GPIO_InitTypeDef gpio_init = {0};
    gpio_init.Pin = LL_GPIO_PIN_8;
    gpio_init.Mode = LL_GPIO_MODE_ALTERNATE;
    gpio_init.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
    gpio_init.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    gpio_init.Pull = LL_GPIO_PULL_NO;
    gpio_init.Alternate = LL_GPIO_AF_1;
    LL_GPIO_Init(GPIOA, &gpio_init);

    gpio_init.Pin = LL_GPIO_PIN_13;
    LL_GPIO_Init(GPIOB, &gpio_init);

    // Вхід аварійного захисту BKIN (PA6, AF1, внутрішня підтяжка до землі)
    gpio_init.Pin = LL_GPIO_PIN_6;
    gpio_init.Pull = LL_GPIO_PULL_DOWN;
    LL_GPIO_Init(GPIOA, &gpio_init);

    // 3. Базове налаштування лічильника (Center-aligned Mode 1, симетричний рахунок)
    uint32_t arr_period = timer_clk_hz / (2 * pwm_freq_hz);
    LL_TIM_InitTypeDef tim_base = {0};
    tim_base.Prescaler = 0;
    tim_base.CounterMode = LL_TIM_COUNTERMODE_CENTER_UP_DOWN;
    tim_base.Autoreload = arr_period - 1;
    tim_base.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
    tim_base.RepetitionCounter = 0;
    LL_TIM_Init(TIM1, &tim_base);

    // 4. Налаштування каналу 1 (PWM Mode 1 з увімкненим Preload)
    LL_TIM_OC_InitTypeDef oc_init = {0};
    oc_init.OCMode = LL_TIM_OCMODE_PWM1;
    oc_init.OCState = LL_TIM_OCSTATE_ENABLE;
    oc_init.OCNState = LL_TIM_OCNSTATE_ENABLE;
    oc_init.OCPolarity = LL_TIM_OCPOLARITY_HIGH;
    oc_init.OCNPolarity = LL_TIM_OCNPOLARITY_HIGH;
    oc_init.OCIdleState = LL_TIM_OCIDLESTATE_LOW;
    oc_init.OCNIdleState = LL_TIM_OCIDLESTATE_LOW;
    oc_init.CompareValue = arr_period / 2; // Початковий коефіцієнт заповнення 50%
    LL_TIM_OC_Init(TIM1, LL_TIM_CHANNEL_CH1, &oc_init);
    LL_TIM_OC_EnablePreload(TIM1, LL_TIM_CHANNEL_CH1);

    // 5. Конфігурація регістра BDTR (Dead-Time, Break Input та захист Lock)
    uint8_t dtg_val = stm32_calc_deadtime_dtg(dead_time_ns, timer_clk_hz);
    
    LL_TIM_BDTR_InitTypeDef bdtr_init = {0};
    bdtr_init.OSSRState = LL_TIM_OSSR_ENABLE;        // Стан виходів при активному таймері та MOE=0
    bdtr_init.OSSIState = LL_TIM_OSSI_ENABLE;        // Стан виходів при зупиненому таймері та MOE=0
    bdtr_init.LockLevel = LL_TIM_LOCKLEVEL_1;        // Захист бітів DTG від програмного збою
    bdtr_init.DeadTime = dtg_val;
    bdtr_init.BreakState = LL_TIM_BREAK_ENABLE;      // Увімкнення апаратного аварійного входу
    bdtr_init.BreakPolarity = LL_TIM_BREAK_POLARITY_HIGH; // Аварія при високому рівні на PA6
    bdtr_init.BreakFilter = LL_TIM_BREAK_FILTER_FDIV1_N4; // Фільтрація перешкод на 4 такти
    bdtr_init.AutomaticOutput = LL_TIM_AUTOMATIC_OUTPUT_DISABLE; // Блокування до явного скидання
    LL_TIM_BDTR_Init(TIM1, &bdtr_init);

    // 6. Увімкнення генерації події автооновлення, головного виходу та запуск таймера
    LL_TIM_EnableARRPreload(TIM1);
    LL_TIM_EnableAllOutputs(TIM1); // Встановлення біта MOE
    LL_TIM_EnableCounter(TIM1);
}

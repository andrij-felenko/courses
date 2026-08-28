#include "stm32f4xx.h"

namespace hal::timer {

struct hardware_timer3 {
    static void init() {
        // 1. Увімкнення тактування
        RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
        (void)RCC->APB1ENR;

        // 2. Альтернативна функція піна PA6
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        (void)RCC->AHB1ENR;
        GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xFu << (6 * 4))) | (2u << (6 * 4));
        GPIOA->MODER  = (GPIOA->MODER  & ~(3u << (6 * 2))) | (2u << (6 * 2));

        // 3. База часу
        TIM3->PSC = psc_val;
        TIM3->ARR = arr_val;

        // 4. ШІМ канал 1
        TIM3->CCR1  = ccr_val;
        TIM3->CCMR1 = (6u << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE;
        TIM3->CCER |= TIM_CCER_CC1E;

        // 5. Буферизація ARR
        TIM3->CR1 |= TIM_CR1_ARPE;

        // 6. Оновлення тіней
        TIM3->CR1 |= TIM_CR1_URS;
        TIM3->EGR  = TIM_EGR_UG;
        TIM3->SR   = ~TIM_SR_UIF;

        // 7. Дозвіл переривань
        TIM3->DIER |= TIM_DIER_UIE;
        NVIC_SetPriority(TIM3_IRQn, 5);
        NVIC_EnableIRQ(TIM3_IRQn);

        // 8. Старт лічби
        TIM3->CR1 |= TIM_CR1_CEN;
    }
};

} // namespace hal::timer

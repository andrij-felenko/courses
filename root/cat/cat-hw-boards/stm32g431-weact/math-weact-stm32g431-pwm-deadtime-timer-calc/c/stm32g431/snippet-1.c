#include "stm32g4xx.h"

void TIM1_PWM_Init(void)
{
    // 1. Увімкнення тактування таймера TIM1
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;

    // 2. Налаштування преддільника PSC та регістру автоперезавантаження ARR
    TIM1->PSC = 0;                  // f_CNT = 170 МГц
    TIM1->ARR = 850;                // f_PWM = 100 кГц при симетричному відліку

    // 3. Конфігурація режиму двонапрямленого відліку (Center-aligned mode 1)
    TIM1->CR1 &= ~TIM_CR1_DIR;
    TIM1->CR1 = (TIM1->CR1 & ~TIM_CR1_CMS) | (1 << TIM_CR1_CMS_Pos); // CMS = 01

    // 4. Встановлення дільника тактування CKD = 00 (t_DTS = t_TIM = 5.882 нс)
    TIM1->CR1 &= ~TIM_CR1_CKD;

    // 5. Конфігурація ШІМ режиму 1 для каналу 1 (CH1 та CH1N)
    TIM1->CCMR1 &= ~TIM_CCMR1_OC1M;
    TIM1->CCMR1 |= (6 << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE; // PWM mode 1

    // 6. Увімкнення комплементарних виходів CH1 та CH1N
    TIM1->CCER |= TIM_CCER_CC1E | TIM_CCER_CC1NE;

    // 7. Налаштування мертвого часу (DTG = 0x22 -> 200 нс) та увімкнення Main Output Enable (MOE)
    TIM1->BDTR &= ~TIM_BDTR_DTG;
    TIM1->BDTR |= (0x22 << TIM_BDTR_DTG_Pos);
    TIM1->BDTR |= TIM_BDTR_MOE;

    // 8. Запуск лічильника таймера
    TIM1->CR1 |= TIM_CR1_CEN;
}

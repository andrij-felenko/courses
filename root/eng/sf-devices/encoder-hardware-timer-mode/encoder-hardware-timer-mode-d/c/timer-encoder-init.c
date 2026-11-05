#include "stm32f4xx.h"

// Ініціалізація таймера TIM2 у режимі квадратурного декодера (x4)
void timer_encoder_init(void) {
    // 1. Увімкнення тактування GPIOA та TIM2
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    // 2. Налаштування PA0 (TIM2_CH1) та PA1 (TIM2_CH2) в режим альтернативної функції (AF1)
    GPIOA->MODER &= ~(GPIO_MODER_MODE0 | GPIO_MODER_MODE1);
    GPIOA->MODER |= (GPIO_MODER_MODE0_1 | GPIO_MODER_MODE1_1); // AF mode
    GPIOA->PUPDR &= ~(GPIO_PUPDR_PUPD0 | GPIO_PUPDR_PUPD1);
    GPIOA->PUPDR |= (GPIO_PUPDR_PUPD0_0 | GPIO_PUPDR_PUPD1_0); // Pull-up

    GPIOA->AFR[0] &= ~(GPIO_AFRL_AFSEL0 | GPIO_AFRL_AFSEL1);
    GPIOA->AFR[0] |= (1 << (0 * 4)) | (1 << (1 * 4)); // AF1 для TIM2

    // 3. Конфігурація каналів вводу TI1 та TI2 у регістрі CCMR1
    TIM2->CCMR1 &= ~(TIM_CCMR1_CC1S | TIM_CCMR1_CC2S);
    TIM2->CCMR1 |= (TIM_CCMR1_CC1S_0 | TIM_CCMR1_CC2S_0); // CC1 mapped to TI1, CC2 mapped to TI2

    // 4. Налаштування цифрового фільтра шуму (N=8 вибірок)
    TIM2->CCMR1 &= ~(TIM_CCMR1_IC1F | TIM_CCMR1_IC2F);
    TIM2->CCMR1 |= (TIM_CCMR1_IC1F_0 | TIM_CCMR1_IC1F_1); // IC1F = 0011
    TIM2->CCMR1 |= (TIM_CCMR1_IC2F_0 | TIM_CCMR1_IC2F_1); // IC2F = 0011

    // 5. Вибір полярності сигналів (без інверсії)
    TIM2->CCER &= ~(TIM_CCER_CC1P | TIM_CCER_CC1NP | TIM_CCER_CC2P | TIM_CCER_CC2NP);

    // 6. Вибір режиму Encoder Mode 3 (x4) у регістрі SMCR
    TIM2->SMCR &= ~TIM_SMCR_SMS;
    TIM2->SMCR |= (TIM_SMCR_SMS_0 | TIM_SMCR_SMS_1); // SMS = 011 (Encoder mode 3)

    // 7. Встановлення максимального значення ARR (32-бітний таймер)
    TIM2->ARR = 0xFFFFFFFFU;

    // 8. Скидання лічильника та запуск таймера
    TIM2->CNT = 0;
    TIM2->CR1 |= TIM_CR1_CEN;
}

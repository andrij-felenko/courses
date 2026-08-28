#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

/* Розрахункові константи часової бази (168 МГц системний такт TIM1) */
#define TIM1_CLK_HZ       168000000UL
#define PWM_FREQ_HZ           20000UL   /* 20 кГц ШІМ */
#define PWM_PERIOD_TICKS  (TIM1_CLK_HZ / PWM_FREQ_HZ) /* 8400 тактів */
#define PWM_DUTY_TICKS    ((PWM_PERIOD_TICKS * 40UL) / 100UL) /* 40% = 3360 */

static volatile uint32_t s_captured_period = 0;
static volatile uint32_t s_capture_ready   = 0;

void timer_driver_init(void)
{
    /* 1. Тактування порту GPIOA та таймера TIM1 */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;
    (void)RCC->APB2ENR; /* Бар'єр синхронізації шини */

    /* 2. Налаштування пінів: PA8 -> TIM1_CH1 (AF1), PA9 -> TIM1_CH2 (AF1) */
    GPIOA->MODER &= ~((3U << (8 * 2)) | (3U << (9 * 2)));
    GPIOA->MODER |=  ((2U << (8 * 2)) | (2U << (9 * 2))); /* Альтернативна функція */

    GPIOA->AFR[1] &= ~((0xFU << ((8 - 8) * 4)) | (0xFU << ((9 - 8) * 4)));
    GPIOA->AFR[1] |=  ((1U << ((8 - 8) * 4)) | (1U << ((9 - 8) * 4))); /* AF1 */

    GPIOA->OSPEEDR |= ((3U << (8 * 2)) | (3U << (9 * 2))); /* High-Speed */

    /* 3. Базова конфігурація лічильника */
    TIM1->PSC = 0;                                 /* Дільник ÷1 (168 МГц) */
    TIM1->ARR = (uint32_t)(PWM_PERIOD_TICKS - 1);  /* 8399 -> період 50 мкс */
    TIM1->CR1 = TIM_CR1_ARPE;                      /* Буферизація ARR */

    /* 4. Канал 1: Вихід ШІМ (PWM Mode 1) */
    TIM1->CCR1 = PWM_DUTY_TICKS;
    TIM1->CCMR1 &= ~TIM_CCMR1_OC1M_Msk;
    TIM1->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos)      /* PWM Mode 1 */
                |  TIM_CCMR1_OC1PE;                /* Preload увімкнено */
    TIM1->CCER  |= TIM_CCER_CC1E;                  /* Дозвіл виходу каналу 1 */

    /* 5. Канал 2: Вхідне захоплення (Input Capture на наростаючий фронт) */
    TIM1->CCMR1 &= ~TIM_CCMR1_CC2S_Msk;
    TIM1->CCMR1 |= (1U << TIM_CCMR1_CC2S_Pos)      /* Канал 2 з'єднаний з TI2 */
                |  (4U << TIM_CCMR1_IC2F_Pos);     /* Цифровий фільтр: N=6 тактів */
    TIM1->CCER  &= ~(TIM_CCER_CC2P | TIM_CCER_CC2NP); /* Наростаючий фронт */
    TIM1->CCER  |= TIM_CCER_CC2E;                  /* Дозвіл захоплення */

    /* 6. Налаштування переривань */
    TIM1->DIER |= TIM_DIER_CC2IE | TIM_DIER_UIE;   /* Переривання захоплення та оновлення */
    NVIC_SetPriority(TIM1_CC_IRQn, 2);
    NVIC_EnableIRQ(TIM1_CC_IRQn);

    /* 7. Активація виходів розширеного таймера та запуск лічби */
    TIM1->BDTR |= TIM_BDTR_MOE;                    /* Main Output Enable */
    TIM1->EGR   = TIM_EGR_UG;                      /* Оновлення тіней */
    TIM1->SR    = 0;                               /* Очищення початкових прапорців */
    TIM1->CR1  |= TIM_CR1_CEN;                     /* Старт лічильника */
}

void TIM1_CC_IRQHandler(void)
{
    /* Перевірка прапорця захоплення каналу 2 */
    if (TIM1->SR & TIM_SR_CC2IF) {
        /* Атомарне скидання прапорця прямим записом інверсної маски */
        TIM1->SR = ~TIM_SR_CC2IF;

        /* Зчитування мітки часу (апаратно очищає прапорець при читанні) */
        s_captured_period = TIM1->CCR2;
        s_capture_ready   = 1;
    }
}

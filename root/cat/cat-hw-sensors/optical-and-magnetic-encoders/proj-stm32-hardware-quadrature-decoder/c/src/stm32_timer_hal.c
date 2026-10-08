#include "../include/stm32_timer_hal.h"
#include <stddef.h>

/* Симуляція екземплярів EXTI для вбудованої системи */
static EXTI_TypeDef g_exti_registers = {0};
EXTI_TypeDef *EXTI = &g_exti_registers;

bool stm32_timer_encoder_init(const stm32_timer_config_t *config) {
    if (config == NULL || config->timer == NULL) {
        return false;
    }

    TIM_TypeDef *TIMx = config->timer;

    /* 1. Вимикаємо таймер перед налаштуванням регістрів */
    TIMx->CR1 &= ~TIM_CR1_CEN;

    /* 2. Конфігурація режиму квадратурного декодера Encoder Mode 3 (SMCR -> SMS = 011b)
       У цьому режимі таймер підраховує фронти і зрізи на ОБОХ каналах TI1 та TI2 (x4 декодування) */
    uint32_t smcr = TIMx->SMCR;
    smcr &= ~TIM_SMCR_SMS_Msk;
    smcr |= TIM_SMCR_SMS_ENCODER3;
    TIMx->SMCR = smcr;

    /* 3. Конфігурація вхідних каналів CH1 (TI1) та CH2 (TI2) в регістрі CCMR1 */
    uint32_t ccmr1 = TIMx->CCMR1;

    /* Прив'язка вхідних каналів: IC1 -> TI1, IC2 -> TI2 */
    ccmr1 &= ~(TIM_CCMR1_CC1S_Msk | TIM_CCMR1_CC2S_Msk);
    ccmr1 |= TIM_CCMR1_CC1S_INPUT_TI1 | TIM_CCMR1_CC2S_INPUT_TI2;

    /* Налаштування цифрової фільтрації вхідних сигналів (ICF) для приглушення завад */
    ccmr1 &= ~(TIM_CCMR1_IC1F_Msk | TIM_CCMR1_IC2F_Msk);
    ccmr1 |= ((uint32_t)config->filter_ch1 << TIM_CCMR1_IC1F_Pos) & TIM_CCMR1_IC1F_Msk;
    ccmr1 |= ((uint32_t)config->filter_ch2 << TIM_CCMR1_IC2F_Pos) & TIM_CCMR1_IC2F_Msk;

    TIMx->CCMR1 = ccmr1;

    /* 4. Налаштування полярності сигналів у регістрі CCER */
    uint32_t ccer = TIMx->CCER;
    ccer &= ~(TIM_CCER_CC1P | TIM_CCER_CC2P);
    if (config->polarity_ch1 == TIM_ENCODER_POLARITY_FALLING) {
        ccer |= TIM_CCER_CC1P;
    }
    if (config->polarity_ch2 == TIM_ENCODER_POLARITY_FALLING) {
        ccer |= TIM_CCER_CC2P;
    }
    TIMx->CCER = ccer;

    /* 5. Встановлення межі лічильника (Auto-reload value) та преддільника */
    TIMx->ARR = config->auto_reload ? config->auto_reload : 0xFFFFU;
    TIMx->PSC = 0U; /* Квадратурний сигнал без попереднього ділення */

    /* 6. Увімкнення переривання оновлення (Update Interrupt Enable) для обробки 16-бітного переповнення */
    TIMx->DIER |= TIM_DIER_UIE;

    /* 7. Скидання лічильника та очищення прапорця переривання */
    TIMx->CNT = 0U;
    TIMx->SR &= ~TIM_SR_UIF;

    /* 8. Запуск таймера */
    TIMx->CR1 |= TIM_CR1_CEN;

    return true;
}

bool stm32_timer_exti_z_init(const stm32_timer_config_t *config) {
    if (config == NULL || config->exti_line == 0U) {
        return false;
    }

    /* Налаштування контролера EXTI для зчитування індексного імпульсу Z (Rising edge trigger) */
    EXTI->IMR |= config->exti_line;   /* Розблокування маски переривання */
    EXTI->RTSR |= config->exti_line;  /* Активація спрацьовування за наростаючим фронтом */
    EXTI->FTSR &= ~config->exti_line; /* Деактивація зрізу */

    return true;
}

bool stm32_timer_check_and_clear_update_flag(TIM_TypeDef *timer) {
    if (timer == NULL) {
        return false;
    }

    if ((timer->SR & TIM_SR_UIF) != 0U) {
        timer->SR &= ~TIM_SR_UIF; /* Очищення прапорця записом 0 */
        return true;
    }

    return false;
}

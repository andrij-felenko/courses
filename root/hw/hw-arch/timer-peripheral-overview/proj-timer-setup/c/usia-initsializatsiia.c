#include "stm32f4xx.h"   /* CMSIS: описи TIM3, RCC, GPIOA, NVIC і назви бітів */

void tim3_init(void)
{
    /* 1 — такт периферії; без нього наступні записи впадуть у порожнечу */
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    (void)RCC->APB1ENR;

    /* 2 — ніжка PA6 віддається каналу 1 (альтернативна функція 2) */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    (void)RCC->AHB1ENR;
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xFu << (6 * 4))) | (2u << (6 * 4));
    GPIOA->MODER  = (GPIOA->MODER  & ~(3u << (6 * 2))) | (2u << (6 * 2));

    /* 3 — часова база: обидва регістри зберігають «на одиницю менше» */
    TIM3->PSC = PSC_VAL;    /* 83  → ділити на 84  → тік 1 мкс   */
    TIM3->ARR = ARR_VAL;    /* 999 → 1000 тіків    → період 1 мс */

    /* 4 — канал 1: ШІМ, високий рівень перші 250 тіків із 1000 */
    TIM3->CCR1  = CCR_VAL;
    TIM3->CCMR1 = (6u << TIM_CCMR1_OC1M_Pos)   /* 110 — ШІМ, режим 1     */
                | TIM_CCMR1_OC1PE;             /* поріг теж через тінь   */
    TIM3->CCER |= TIM_CCER_CC1E;               /* вивести канал на ніжку */

    /* 5 — межа міняється тільки на межі періоду */
    TIM3->CR1 |= TIM_CR1_ARPE;

    /* 6 — перенести PSC/ARR/CCR у тіні негайно, не турбуючи переривання */
    TIM3->CR1 |= TIM_CR1_URS;
    TIM3->EGR  = TIM_EGR_UG;
    TIM3->SR   = ~TIM_SR_UIF;

    /* 7 — дозволити переривання: спершу в таймері, потім у контролері */
    TIM3->DIER |= TIM_DIER_UIE;
    NVIC_SetPriority(TIM3_IRQn, 5);
    NVIC_EnableIRQ(TIM3_IRQn);

    /* 8 — і тільки тепер пустити лічбу */
    TIM3->CR1 |= TIM_CR1_CEN;
}

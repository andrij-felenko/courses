/* Апаратна обв'язка стенда: 168 МГц із 5 тактами очікування Flash,
 * TIM1 у центрованому режимі на 20 кГц і АЦП, який запускає САМ таймер.
 */
#ifndef BSP_H
#define BSP_H

#include <stdbool.h>
#include <stdint.h>
#include "foc.h"
#include "stm32f4xx.h"

#define BSP_SYSCLK_MHZ   168U
#define BSP_PWM_HZ       20000U
/* Центрований лічильник проходить період двічі: 168e6 / (2 * 4200) = 20 кГц. */
#define BSP_PWM_ARR      4200U
/* Шунт 10 мОм, підсилювач x20, опора 3.3 В, 12 біт: код -> ампери. */
#define BSP_ADC_TO_A     (3.3f / 4096.0f / (0.01f * 20.0f))

bool bsp_clock_init(void);   /* false — кварц або PLL не завелися */
void bsp_pwm_init(void);
void bsp_adc_init(void);

static inline void bsp_set_duties(duty3_t d)
{
    /* Шпаруватості вже затиснуті в [0.02; 0.98], тож перетворення безпечне.
       Регістри CCR із попереднім завантаженням: значення набудуть чинності
       разом, на найближчій події оновлення таймера. */
    TIM1->CCR1 = (uint32_t)(d.a * (float)BSP_PWM_ARR);
    TIM1->CCR2 = (uint32_t)(d.b * (float)BSP_PWM_ARR);
    TIM1->CCR3 = (uint32_t)(d.c * (float)BSP_PWM_ARR);
}

static inline void bsp_ack_adc(void)
{
    /* Прапорці АЦП скидаються записом нуля; решту бітів не чіпаємо. */
    ADC1->SR = ~(uint32_t)(ADC_SR_JEOC | ADC_SR_JSTRT);
}

static inline void bsp_trip(void)
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   /* аварійно зняти напругу з мосту */
}

#endif /* BSP_H */

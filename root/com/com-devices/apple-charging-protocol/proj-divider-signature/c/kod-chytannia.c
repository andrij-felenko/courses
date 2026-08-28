#include <stdint.h>
#include <stdbool.h>
#include "stm32f1xx.h"

/* Лінії підпису заведено на два аналогові входи:
   D+ → PA0 (ADC12_IN0),  D− → PA1 (ADC12_IN1). */
#define CH_DP    0u
#define CH_DM    1u
#define VREF_MV  3300

static void dline_adc_init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN | RCC_APB2ENR_ADC1EN;

    /* PA0 і PA1 — аналоговий режим (CNF=00, MODE=00). Це вимикає тригер Шмітта
       й від'єднує підтяжки. Будь-який інший режим виводу сам зруйнує підпис —
       навіть «нешкідливий» цифровий вхід із внутрішньою підтяжкою на 40 кОм. */
    GPIOA->CRL &= ~0xFFu;

    /* Такт АЦП не вище 14 МГц: 72 МГц / 6 = 12 МГц. */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_ADCPRE) | RCC_CFGR_ADCPRE_DIV6;

    /* SMP = 7 → 239.5 такту вибірки. Порахували 34.5 як мінімум; беремо
       максимум, бо вимір робиться раз на встромляння і 20 мкс тут — ніщо. */
    ADC1->SMPR2 |= (7u << (3 * CH_DP)) | (7u << (3 * CH_DM));

    ADC1->CR2 |= ADC_CR2_ADON;                 /* прокинути АЦП */
    delay_us(10);                              /* t_STAB */
    ADC1->CR2 |= ADC_CR2_RSTCAL;
    while (ADC1->CR2 & ADC_CR2_RSTCAL) { }
    ADC1->CR2 |= ADC_CR2_CAL;                  /* калібрування зсуву */
    while (ADC1->CR2 & ADC_CR2_CAL) { }
}

static uint16_t adc_read_raw(uint32_t ch)
{
    ADC1->SQR3 = ch;                           /* послідовність з однієї конверсії */
    ADC1->CR2 |= ADC_CR2_ADON;                 /* у F1 повторний ADON — це старт */
    while (!(ADC1->SR & ADC_SR_EOC)) { }
    return (uint16_t)ADC1->DR;                 /* читання DR скидає EOC */
}

/* Медіана з п'яти. Не середнє: середнє зсувається від одного викиду, медіана —
   ні. Проти недобору вибірки не помагає ні те, ні те — його вже прибрано
   часом вибірки вище. */
static int dline_read_mv(uint32_t ch)
{
    uint16_t s[5];
    for (int i = 0; i < 5; i++)
        s[i] = adc_read_raw(ch);

    for (int i = 1; i < 5; i++) {              /* сортування вставками */
        uint16_t v = s[i];
        int j = i - 1;
        while (j >= 0 && s[j] > v) { s[j + 1] = s[j]; j--; }
        s[j + 1] = v;
    }
    return (int)((uint32_t)s[2] * VREF_MV / 4095u);
}

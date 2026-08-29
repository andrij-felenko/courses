/* Фаза 4: вимірювання реальної напруги VDDA через внутрішнє опорне джерело.
   Ідея проста: VREFINT стабільне, а сходинка АЦП пропорційна VDDA. Отже, чим
   меншим кодом виміряне незмінне джерело, тим вища напруга живлення. */
#include "bringup.h"
#include "stm32f4_regs.h"

#define VREF_NOMINAL_MV   1210U    /* типове VREFINT для F4, якщо константи немає */
#define ADC_FULL_SCALE    4095U    /* 12 біт */
#define ADC_CAL_VDDA_MV   3300U    /* напруга, при якій знято заводську константу */
#define ADC_STAB_US       20U      /* tSTAB опорного джерела після ADON */
#define ADC_EOC_TRIES     100000U

bringup_status_t bringup_measure_vdda(bringup_report_t *report)
{
    uint32_t tries;
    uint16_t raw;
    uint16_t cal;

    RCC_APB2ENR |= RCC_APB2ENR_ADC1EN;
    (void)RCC_APB2ENR;

    /* Дільник /4: при PCLK2 16 МГц дає 4 МГц — усередині дозволеного.
       TSVREFE підключає внутрішній канал VREFINT до входу мультиплексора. */
    ADC_CCR = (ADC_CCR & ~ADC_CCR_ADCPRE_MASK)
            | ADC_CCR_ADCPRE_DIV4
            | ADC_CCR_TSVREFE;

    /* Канал 17 живиться через високий внутрішній опір: йому потрібно щонайменше
       10 мкс вибірки, тому беремо максимальні 480 тактів (поле 3 біти = 0b111). */
    ADC1_SMPR1 |= (7U << ((ADC_CHANNEL_VREFINT - 10U) * 3U));

    ADC1_CR1 = 0U;             /* 12 біт, без сканування й переривань */
    ADC1_SQR1 = 0U;            /* довжина послідовності — один канал */
    ADC1_SQR3 = ADC_CHANNEL_VREFINT;

    ADC1_CR2 |= ADC_CR2_ADON;
    bringup_delay_us(ADC_STAB_US);

    ADC1_SR = 0U;
    ADC1_CR2 |= ADC_CR2_SWSTART;

    tries = ADC_EOC_TRIES;
    while ((ADC1_SR & ADC_SR_EOC) == 0U && tries > 0U) {
        --tries;
    }
    if (tries == 0U) {
        ADC1_CR2 &= ~ADC_CR2_ADON;
        report->adc_status = BRINGUP_ERR_ADC_TIMEOUT;
        return BRINGUP_ERR_ADC_TIMEOUT;
    }

    raw = (uint16_t)(ADC1_DR & 0x0FFFU);   /* читання DR знімає EOC */
    ADC1_CR2 &= ~ADC_CR2_ADON;
    report->vrefint_raw = raw;

    if (raw == 0U) {
        /* Нуль на стабільному джерелі означає, що аналогова частина мертва:
           обірвана VDDA після феритової бусини або пробитий вхід. */
        report->adc_status = BRINGUP_ERR_ADC_TIMEOUT;
        return BRINGUP_ERR_ADC_TIMEOUT;
    }

    cal = *(const volatile uint16_t *)(uintptr_t)VREFINT_CAL_ADDR;
    report->vrefint_cal = cal;

    if (cal != 0U && cal != 0xFFFFU) {
        /* VDDA = 3.30 В · ADC_CAL / ADC_DATA — рахуємо в мілівольтах цілими. */
        report->vdda_mv = (ADC_CAL_VDDA_MV * (uint32_t)cal) / (uint32_t)raw;
        report->adc_status = BRINGUP_OK;
        return BRINGUP_OK;
    }

    /* Комірка не запрограмована (трапляється на F405/F407): лишається лише
       типове значення джерела, тож точність падає з 1% до кількох відсотків. */
    report->vdda_mv = (ADC_FULL_SCALE * VREF_NOMINAL_MV) / (uint32_t)raw;
    report->adc_status = BRINGUP_ERR_VREF_UNCALIBRATED;
    return BRINGUP_ERR_VREF_UNCALIBRATED;
}

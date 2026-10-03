#include "adc_opamp.hpp"

namespace foc {

AdcOpampDriver::AdcOpampDriver(float current_scale)
    : current_scale_(current_scale) {}

bool AdcOpampDriver::init() {
    configureOPAMP();
    configureADC();
    return true;
}

void AdcOpampDriver::configureOPAMP() {
#ifdef OPAMP1
    // Увімкнення тактування системної конфігурації SYSCFG/OPAMP
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    // Налаштування OPAMP1 у режим PGA (підсилення з фіксованим коефіцієнтом Gain = 8)
    OPAMP1->CSR = (3u << OPAMP_CSR_PGA_GAIN_Pos) | OPAMP_CSR_OPAMPEN;
    // Налаштування OPAMP2 у режим PGA (Gain = 8)
    OPAMP2->CSR = (3u << OPAMP_CSR_PGA_GAIN_Pos) | OPAMP_CSR_OPAMPEN;
#endif
}

void AdcOpampDriver::configureADC() {
#ifdef ADC1
    // Увімкнення тактування ADC1 та ADC2
    RCC->AHB2ENR |= RCC_AHB2ENR_ADC12EN;

    // Вихід з режиму глибокого сну та увімкнення регулятора напруги АЦП
    ADC1->CR &= ~ADC_CR_DEEPPWD;
    ADC2->CR &= ~ADC_CR_DEEPPWD;
    ADC1->CR |= ADC_CR_ADVREGEN;
    ADC2->CR |= ADC_CR_ADVREGEN;

    // Затримка на стабілізацію регулятора напруги АЦП (10 мкс)
    for (volatile int i = 0; i < 1700; ++i) { __NOP(); }

    // Виконання калібрування АЦП1 та АЦП2
    ADC1->CR |= ADC_CR_ADCAL;
    while (ADC1->CR & ADC_CR_ADCAL) {}

    ADC2->CR |= ADC_CR_ADCAL;
    while (ADC2->CR & ADC_CR_ADCAL) {}

    // Увімкнення ADC1 та ADC2
    ADC1->ISR |= ADC_ISR_ADRDY;
    ADC1->CR |= ADC_CR_ADEN;
    while (!(ADC1->ISR & ADC_ISR_ADRDY)) {}

    ADC2->ISR |= ADC_ISR_ADRDY;
    ADC2->CR |= ADC_CR_ADEN;
    while (!(ADC2->ISR & ADC_ISR_ADRDY)) {}

    // Конфігурація інжектованого каналу ADC1 (вхід від OPAMP1 out, тригер TIM1 TRGO2)
    ADC1->JSQR = (1u << ADC_JSQR_JL_Pos) |
                 (9u << ADC_JSQR_JEXTSEL_Pos) |
                 (1u << ADC_JSQR_JEXTEN_Pos) |
                 (3u << ADC_JSQR_JSQ1_Pos);

    // Конфігурація інжектованого каналу ADC2 (вихід OPAMP2)
    ADC2->JSQR = (1u << ADC_JSQR_JL_Pos) |
                 (9u << ADC_JSQR_JEXTSEL_Pos) |
                 (1u << ADC_JSQR_JEXTEN_Pos) |
                 (4u << ADC_JSQR_JSQ1_Pos);

    // Увімкнення переривання після закінчення інжектованого перетворення (JEOC)
    ADC1->IER |= ADC_IER_JEOCIE;
    NVIC_EnableIRQ(ADC1_2_IRQn);
    NVIC_SetPriority(ADC1_2_IRQn, 0);
#endif
}

void AdcOpampDriver::calibrateOffsets(uint16_t num_samples) {
    uint32_t sum_a = 0;
    uint32_t sum_b = 0;

    for (uint16_t i = 0; i < num_samples; ++i) {
#ifdef ADC1
        // Програмний запуск інжектованої конверсії для автокалібрування
        ADC1->CR |= ADC_CR_JADSTART;
        ADC2->CR |= ADC_CR_JADSTART;

        while (!(ADC1->ISR & ADC_ISR_JEOC)) {}
        while (!(ADC2->ISR & ADC_ISR_JEOC)) {}

        sum_a += ADC1->JDR1;
        sum_b += ADC2->JDR1;

        ADC1->ISR |= ADC_ISR_JEOC;
        ADC2->ISR |= ADC_ISR_JEOC;
#else
        sum_a += 2048;
        sum_b += 2048;
#endif
    }

    offset_a_ = static_cast<float>(sum_a) / static_cast<float>(num_samples);
    offset_b_ = static_cast<float>(sum_b) / static_cast<float>(num_samples);
    calibrated_ = true;
}

void AdcOpampDriver::readRawSamples(uint16_t& raw_a, uint16_t& raw_b) {
#ifdef ADC1
    raw_adc_a_ = static_cast<uint16_t>(ADC1->JDR1);
    raw_adc_b_ = static_cast<uint16_t>(ADC2->JDR1);
#endif
    raw_a = raw_adc_a_;
    raw_b = raw_adc_b_;
}

void AdcOpampDriver::getPhaseCurrents(float& i_a, float& i_b) {
    uint16_t raw_a = 0, raw_b = 0;
    readRawSamples(raw_a, raw_b);

    // Розрахунок струму: I = (ADC_RAW - OFFSET) * SCALE
    i_a = (static_cast<float>(raw_a) - offset_a_) * current_scale_;
    i_b = (static_cast<float>(raw_b) - offset_b_) * current_scale_;
}

} // namespace foc

#include "tim1_pwm.hpp"

namespace foc {

Tim1PwmDriver::Tim1PwmDriver(uint32_t pwm_freq_hz, uint16_t dead_time_ns)
    : pwm_frequency_hz_(pwm_freq_hz), dead_time_ns_(dead_time_ns) {}

bool Tim1PwmDriver::init() {
    configureGPIO();
    configureTimerRegisters();
    initialized_ = true;
    return true;
}

void Tim1PwmDriver::configureGPIO() {
#ifdef TIM1
    // Увімкнення тактування портів GPIOA та GPIOB
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN;

    // Налаштування пінів PA8 (CH1), PA9 (CH2), PA10 (CH3) на режим альтернативної функції AF6 (TIM1)
    GPIOA->MODER &= ~(GPIO_MODER_MODE8_Msk | GPIO_MODER_MODE9_Msk | GPIO_MODER_MODE10_Msk);
    GPIOA->MODER |= (2u << GPIO_MODER_MODE8_Pos) | (2u << GPIO_MODER_MODE9_Pos) | (2u << GPIO_MODER_MODE10_Pos);
    GPIOA->AFR[1] &= ~(GPIO_AFRH_AFSEL8_Msk | GPIO_AFRH_AFSEL9_Msk | GPIO_AFRH_AFSEL10_Msk);
    GPIOA->AFR[1] |= (6u << GPIO_AFRH_AFSEL8_Pos) | (6u << GPIO_AFRH_AFSEL9_Pos) | (6u << GPIO_AFRH_AFSEL10_Pos);
    GPIOA->OSPEEDR |= (3u << GPIO_OSPEEDR_OSPEED8_Pos) | (3u << GPIO_OSPEEDR_OSPEED9_Pos) | (3u << GPIO_OSPEEDR_OSPEED10_Pos);

    // Налаштування комплементарних пінів PB13 (CH1N), PB14 (CH2N), PB15 (CH3N) на AF6
    GPIOB->MODER &= ~(GPIO_MODER_MODE13_Msk | GPIO_MODER_MODE14_Msk | GPIO_MODER_MODE15_Msk);
    GPIOB->MODER |= (2u << GPIO_MODER_MODE13_Pos) | (2u << GPIO_MODER_MODE14_Pos) | (2u << GPIO_MODER_MODE15_Pos);
    GPIOB->AFR[1] &= ~(GPIO_AFRH_AFSEL13_Msk | GPIO_AFRH_AFSEL14_Msk | GPIO_AFRH_AFSEL15_Msk);
    GPIOB->AFR[1] |= (6u << GPIO_AFRH_AFSEL13_Pos) | (6u << GPIO_AFRH_AFSEL14_Pos) | (6u << GPIO_AFRH_AFSEL15_Pos);
    GPIOB->OSPEEDR |= (3u << GPIO_OSPEEDR_OSPEED13_Pos) | (3u << GPIO_OSPEEDR_OSPEED14_Pos) | (3u << GPIO_OSPEEDR_OSPEED15_Pos);
#endif
}

void Tim1PwmDriver::configureTimerRegisters() {
#ifdef TIM1
    // Увімкнення тактування TIM1 (170 МГц на STM32G431)
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;

    constexpr uint32_t system_clock_hz = 170000000u;
    // Центрований ШІМ (Center-aligned Mode 1): період Т = 2 * ARR * t_clk
    timer_period_counts_ = static_cast<uint16_t>(system_clock_hz / (2u * pwm_frequency_hz_));

    TIM1->PSC = 0; // Без дільника частоти
    TIM1->ARR = timer_period_counts_ - 1;

    // Режим ШІМ 1 (PWM mode 1) для каналів 1, 2, 3 та дозвіл буферизації (Preload Enable)
    TIM1->CCMR1 = (6u << TIM_CCMR1_OC1M_Pos) | TIM_CCMR1_OC1PE | (6u << TIM_CCMR1_OC2M_Pos) | TIM_CCMR1_OC2PE;
    TIM1->CCMR2 = (6u << TIM_CCMR2_OC3M_Pos) | TIM_CCMR2_OC3PE | (6u << TIM_CCMR2_OC4M_Pos) | TIM_CCMR2_OC4PE;

    // Початкові значення коефіцієнтів заповнення (50%)
    TIM1->CCR1 = timer_period_counts_ / 2;
    TIM1->CCR2 = timer_period_counts_ / 2;
    TIM1->CCR3 = timer_period_counts_ / 2;
    // Канал 4 відповідає за тригер запуску АЦП у момент мінімуму/максимуму ШІМ
    TIM1->CCR4 = timer_period_counts_ - 5;

    // Увімкнення прямих та комплементарних виходів (CCxE та CCxNE)
    TIM1->CCER = TIM_CCER_CC1E | TIM_CCER_CC1NE |
                 TIM_CCER_CC2E | TIM_CCER_CC2NE |
                 TIM_CCER_CC3E | TIM_CCER_CC3NE;

    // Конфігурація мертвого часу (BDTR) та виходу тригера TRGO2 на подію CC4
    uint8_t dtg = calculateDeadTimeRegister(dead_time_ns_, system_clock_hz);
    TIM1->BDTR = dtg | TIM_BDTR_MOE;

    // Налаштування TRGO2 на порівняння OC4REF для генерації тригера АЦП
    TIM1->CR2 &= ~TIM_CR2_MMS2;
    TIM1->CR2 |= (0x8u << TIM_CR2_MMS2_Pos);

    // Налаштування центрування відліку (Center-aligned mode 1)
    TIM1->CR1 &= ~TIM_CR1_CMS;
    TIM1->CR1 |= (1u << TIM_CR1_CMS_Pos) | TIM_CR1_ARPE;
#endif
}

uint8_t Tim1PwmDriver::calculateDeadTimeRegister(uint16_t dead_time_ns, uint32_t timer_clock_hz) {
    float t_dt = static_cast<float>(dead_time_ns) * 1e-9f;
    float t_dts = 1.0f / static_cast<float>(timer_clock_hz);
    uint32_t dtg_val = static_cast<uint32_t>(t_dt / t_dts);
    if (dtg_val > 127) {
        dtg_val = 127;
    }
    return static_cast<uint8_t>(dtg_val);
}

void Tim1PwmDriver::start() {
#ifdef TIM1
    TIM1->BDTR |= TIM_BDTR_MOE;
    TIM1->CR1 |= TIM_CR1_CEN;
#endif
}

void Tim1PwmDriver::stop() {
#ifdef TIM1
    TIM1->BDTR &= ~TIM_BDTR_MOE;
    TIM1->CR1 &= ~TIM_CR1_CEN;
#endif
}

void Tim1PwmDriver::setDutyCycles(float duty_a, float duty_b, float duty_c) {
    duty_a = std::clamp(duty_a, 0.0f, 1.0f);
    duty_b = std::clamp(duty_b, 0.0f, 1.0f);
    duty_c = std::clamp(duty_c, 0.0f, 1.0f);

    uint16_t ccr1 = static_cast<uint16_t>(duty_a * static_cast<float>(timer_period_counts_));
    uint16_t ccr2 = static_cast<uint16_t>(duty_b * static_cast<float>(timer_period_counts_));
    uint16_t ccr3 = static_cast<uint16_t>(duty_c * static_cast<float>(timer_period_counts_));

    setPWMCounts(ccr1, ccr2, ccr3);
}

void Tim1PwmDriver::setPWMCounts(uint16_t ccr1, uint16_t ccr2, uint16_t ccr3) {
#ifdef TIM1
    TIM1->CCR1 = ccr1;
    TIM1->CCR2 = ccr2;
    TIM1->CCR3 = ccr3;
#else
    (void)ccr1; (void)ccr2; (void)ccr3;
#endif
}

} // namespace foc

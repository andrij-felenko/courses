#include "inverter.hpp"

extern "C" {
// Символи зі скрипта компонувальника: секція .ramfunc має VMA в SRAM
// і LMA у Flash, тож перед першим викликом її треба перенести.
extern std::uint32_t _sramfunc;
extern std::uint32_t _eramfunc;
extern std::uint32_t _siramfunc;
}

namespace inverter {
namespace {

// Очікування прапорця з лічильником: while без виходу в прошивці не буває.
[[nodiscard]] bool wait_bit(volatile std::uint32_t& reg, std::uint32_t mask, bool want) noexcept
{
    for (std::uint32_t guard = 0U; guard < 500000U; ++guard) {
        if (((reg & mask) != 0U) == want) {
            return true;
        }
    }
    return false;
}

void copy_ramfunc() noexcept
{
    const std::uint32_t* src = &_siramfunc;
    std::uint32_t* dst = &_sramfunc;
    while (dst < &_eramfunc) {
        *dst++ = *src++;
    }
    __DSB();   // записи дійшли до SRAM
    __ISB();   // конвеєр перечитає інструкції з нових адрес
}

void gpio_af(GPIO_TypeDef* port, std::uint32_t pin, std::uint32_t af) noexcept
{
    port->MODER = (port->MODER & ~(0b11U << (pin * 2U))) | (0b10U << (pin * 2U));
    port->OSPEEDR |= (0b11U << (pin * 2U));
    port->AFR[pin >> 3U] = (port->AFR[pin >> 3U] & ~(0xFU << ((pin & 7U) * 4U)))
                         | (af << ((pin & 7U) * 4U));
}

std::expected<void, BringUpError> configure_clock() noexcept
{
    RCC->CR |= RCC_CR_HSEON;
    if (!wait_bit(RCC->CR, RCC_CR_HSERDY, true)) {
        return std::unexpected{BringUpError::HseTimeout};
    }

    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    static_cast<void>(RCC->APB1ENR);
    PWR->CR |= PWR_CR_VOS;   // Scale 1: дозвіл працювати на 168 МГц

    // Спершу затримка Flash, і лише потім частота — інакше ядро почне читати
    // код швидше, ніж масив пам'яті встигає його віддавати. ART (ICEN/DCEN)
    // піднімає середню швидкодію й псує детермінізм, тому критичний код
    // однаково виконується з SRAM.
    FLASH->ACR = FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN
               | FLASH_ACR_LATENCY_5WS;

    RCC->CFGR = RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    // 8 МГц / M(8) = 1 МГц; x N(336) = 336 МГц; / P(2) = 168 МГц; / Q(7) = 48 МГц.
    // Поля PLLCFGR: M[5:0], N[14:6], P[17:16] (00 = /2), Q[27:24].
    RCC->PLLCFGR = (8U << 0) | (336U << 6) | (0U << 16) | (7U << 24)
                 | RCC_PLLCFGR_PLLSRC_HSE;

    RCC->CR |= RCC_CR_PLLON;
    if (!wait_bit(RCC->CR, RCC_CR_PLLRDY, true)) {
        return std::unexpected{BringUpError::PllTimeout};
    }

    RCC->CFGR |= RCC_CFGR_SW_PLL;
    if (!wait_bit(RCC->CFGR, RCC_CFGR_SWS_PLL, true)) {
        return std::unexpected{BringUpError::ClockSwitch};
    }

    SystemCoreClock = kSysclkMhz * 1000000U;
    return {};
}

void configure_pwm() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;
    static_cast<void>(RCC->APB2ENR);

    gpio_af(GPIOA, 8U, 1U);    // CH1  — верхній ключ фази A
    gpio_af(GPIOA, 9U, 1U);    // CH2  — фаза B
    gpio_af(GPIOA, 10U, 1U);   // CH3  — фаза C
    gpio_af(GPIOB, 13U, 1U);   // CH1N — нижні ключі
    gpio_af(GPIOB, 14U, 1U);
    gpio_af(GPIOB, 15U, 1U);

    TIM1->PSC = 0U;
    TIM1->ARR = kPwmArr;
    // RCR = 1: подія оновлення раз на повний період — на дні лічильника,
    // коли всі три верхні ключі відкриті й міст стоїть у нульовому векторі.
    TIM1->RCR = 1U;
    TIM1->CR1 = TIM_CR1_ARPE | TIM_CR1_CMS_0;   // центрований режим 1
    TIM1->CR2 = TIM_CR2_MMS_1;                  // MMS = 010: Update -> TRGO

    TIM1->CCMR1 = (6U << 4) | TIM_CCMR1_OC1PE | (6U << 12) | TIM_CCMR1_OC2PE;
    TIM1->CCMR2 = (6U << 4) | TIM_CCMR2_OC3PE;
    TIM1->CCER = TIM_CCER_CC1E | TIM_CCER_CC1NE
               | TIM_CCER_CC2E | TIM_CCER_CC2NE
               | TIM_CCER_CC3E | TIM_CCER_CC3NE;

    TIM1->CCR1 = kPwmArr / 2U;
    TIM1->CCR2 = kPwmArr / 2U;
    TIM1->CCR3 = kPwmArr / 2U;

    // DTG[7:0] = 108 -> 108 тактів по 5.95 нс, тобто ~643 нс мертвого часу.
    TIM1->BDTR = TIM_BDTR_MOE | (108U << 0);

    TIM1->EGR = TIM_EGR_UG;
    TIM1->CR1 |= TIM_CR1_CEN;
}

void configure_adc() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    static_cast<void>(RCC->APB2ENR);

    GPIOA->MODER |= (0b11U << (0U * 2U)) | (0b11U << (1U * 2U));   // PA0, PA1 — аналог

    ADC->CCR = ADC_CCR_ADCPRE_0;                            // 84 МГц / 4 = 21 МГц
    ADC1->SMPR2 = (1U << (0U * 3U)) | (1U << (1U * 3U));    // по 15 тактів на канал

    // Інжектована послідовність вирівняна по JSQ4: при JL = 1 першим
    // перетворюється JSQ3 (результат у JDR1), другим JSQ4 (у JDR2).
    ADC1->JSQR = (1U << 20) | (0U << 10) | (1U << 15);

    ADC1->CR1 = ADC_CR1_SCAN | ADC_CR1_JEOCIE;

    // JEXTSEL = 0001 — TIM1_TRGO, JEXTEN = 01 — наростаючий фронт. Ланцюг
    // «таймер -> АЦП» замкнено в кремнії, ядро в запуску участі не бере,
    // тому джитер моменту вибірки дорівнює нулю тактів.
    ADC1->CR2 = ADC_CR2_JEXTSEL_0 | ADC_CR2_JEXTEN_0 | ADC_CR2_ADON;

    // Контур струму — найтерміновіше в системі; UART і решта мусять мати
    // числово більший, тобто нижчий, пріоритет.
    NVIC_SetPriority(ADC_IRQn, 0U);
    NVIC_EnableIRQ(ADC_IRQn);
}

}  // namespace

std::expected<void, BringUpError> bring_up() noexcept
{
    copy_ramfunc();   // до першого виклику будь-чого з .ramfunc

    if (auto clocked = configure_clock(); !clocked) {
        return clocked;
    }

    configure_pwm();
    configure_adc();
    return {};
}

}  // namespace inverter

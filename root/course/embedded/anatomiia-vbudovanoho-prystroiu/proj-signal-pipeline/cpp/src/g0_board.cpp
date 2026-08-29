#include "board/g0_board.hpp"

#include "stm32g0xx.h" // заголовок пристрою з CMSIS-пакета STM32CubeG0

namespace {

/// Комірка, куди DMA кладе черговий відлік. Пише її периферія, а не
/// процесор, тож volatile обов'язковий. Лежить поза namespace board, бо її
/// бачать і налаштування каналу, і обробник переривання наприкінці файла.
volatile std::uint16_t g_sample = 0;

} // namespace

namespace board {
namespace {

/// Номер запиту DMAMUX для АЦП на STM32G0 (таблиця запитів у RM0444).
/// Іменованої константи в заголовку пристрою немає.
constexpr std::uint32_t kDmamuxReqAdc1 = 5;
constexpr std::uint32_t kTimeoutLoops = 1'000'000;

std::expected<void, Error> clock_init_48mhz() noexcept
{
    // 48 МГц — це вже друга смуга затримки Flash, один такт очікування.
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_0;

    // PLL від HSI16: M = 1 (поле 0), N = 12, R = 4 (поле 3).
    // 16 МГц / 1 * 12 = 192 МГц у ГКН, / 4 = 48 МГц на виході R.
    RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSI
                 | (0u << RCC_PLLCFGR_PLLM_Pos)
                 | (12u << RCC_PLLCFGR_PLLN_Pos)
                 | (3u << RCC_PLLCFGR_PLLR_Pos)
                 | RCC_PLLCFGR_PLLREN;

    RCC->CR |= RCC_CR_PLLON;
    for (std::uint32_t i = 0; (RCC->CR & RCC_CR_PLLRDY) == 0u; ++i) {
        if (i >= kTimeoutLoops) {
            return std::unexpected{Error::PllTimeout};
        }
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_1; // SW = 010: PLLRCLK
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_1) {
        // апаратне перемикання джерела, кілька тактів
    }
    SystemCoreClock = 48'000'000u;
    return {};
}

void gpio_init() noexcept
{
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;

    // PA0 — аналоговий вхід АЦП (режим 11).
    GPIOA->MODER |= GPIO_MODER_MODE0;

    // PA6 — альтернативна функція AF1 = TIM3_CH1 (режим 10).
    GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODE6) | GPIO_MODER_MODE6_1;
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~GPIO_AFRL_AFSEL6) | (1u << GPIO_AFRL_AFSEL6_Pos);
    GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED6_0; // середня швидкість фронту, менше дзвону
}

void pwm_init() noexcept
{
    RCC->APBENR1 |= RCC_APBENR1_TIM3EN;

    TIM3->PSC = 0u;      // 48 МГц / 65536 ≈ 732 Гц несуча
    TIM3->ARR = 65535u;
    TIM3->CCR1 = 0u;     // стартуємо з вимкненим навантаженням

    // Режим ШІМ 1 (110) із попереднім завантаженням регістра порівняння:
    // без OC1PE запис посеред періоду вкоротив би поточний імпульс.
    TIM3->CCMR1 = TIM_CCMR1_OC1M_2 | TIM_CCMR1_OC1M_1 | TIM_CCMR1_OC1PE;
    TIM3->CCER |= TIM_CCER_CC1E;
    TIM3->CR1 |= TIM_CR1_ARPE;
    TIM3->EGR = TIM_EGR_UG;
    TIM3->CR1 |= TIM_CR1_CEN;
}

void trigger_timer_init() noexcept
{
    RCC->APBENR1 |= RCC_APBENR1_TIM2EN;

    TIM2->PSC = 48u - 1u;                              // лічильник цокає 1 МГц
    TIM2->ARR = (1'000'000u / kSamplePeriodHz) - 1u;   // 10 000 тактів = 10 мс

    // MMS = 010: подія оновлення виходить назовні як TRGO. Саме звідси
    // береться незмінний dt — а не з викликів у нескінченному циклі.
    TIM2->CR2 = TIM_CR2_MMS_1;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->CR1 |= TIM_CR1_CEN;
}

void dma_init() noexcept
{
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;

    DMAMUX1_Channel0->CCR = kDmamuxReqAdc1; // канал 1 DMA1 = канал 0 DMAMUX

    DMA1_Channel1->CPAR = reinterpret_cast<std::uint32_t>(&ADC1->DR);
    DMA1_Channel1->CMAR = reinterpret_cast<std::uint32_t>(&g_sample);
    DMA1_Channel1->CNDTR = 1u;

    // Одна комірка по 16 біт з обох боків, кільцевий режим, переривання
    // завершення передачі. MINC не потрібен: адреса в пам'яті одна.
    DMA1_Channel1->CCR = DMA_CCR_PSIZE_0 | DMA_CCR_MSIZE_0 | DMA_CCR_CIRC | DMA_CCR_TCIE;
    DMA1_Channel1->CCR |= DMA_CCR_EN;

    // Найвищий пріоритет: конвеєр мусить відпрацювати до наступного відліку.
    NVIC_SetPriority(DMA1_Channel1_IRQn, 0);
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);
}

std::expected<void, Error> adc_init() noexcept
{
    RCC->APBENR2 |= RCC_APBENR2_ADCEN;

    ADC1->CFGR2 = ADC_CFGR2_CKMODE_1; // тактування перетворювача PCLK/4 = 12 МГц

    // Стабілізатор АЦП: після ввімкнення потрібна пауза (20 мкс за паспортом).
    ADC1->CR |= ADC_CR_ADVREGEN;
    for (volatile std::uint32_t i = 0; i < 2000u; ++i) {
    }

    // Калібрування обов'язкове: без нього зсув нуля з'їдає молодші розряди.
    ADC1->CR |= ADC_CR_ADCAL;
    for (std::uint32_t i = 0; (ADC1->CR & ADC_CR_ADCAL) != 0u; ++i) {
        if (i >= kTimeoutLoops) {
            return std::unexpected{Error::AdcCalibrationTimeout};
        }
    }

    // Найдовше вікно вибірки (SMP1 = 111, 160.5 такту АЦП): високоомний
    // дільник інакше не встигає зарядити конденсатор вибірки, і напруга
    // виходить заниженою.
    ADC1->SMPR = ADC_SMPR_SMP1;
    ADC1->CHSELR = ADC_CHSELR_CHSEL0; // канал 0 = PA0

    // Зовнішній запуск TRG2 = TIM2_TRGO фронтом наростання, результат — у DMA.
    ADC1->CFGR1 = (2u << ADC_CFGR1_EXTSEL_Pos) | ADC_CFGR1_EXTEN_0
                | ADC_CFGR1_DMAEN | ADC_CFGR1_DMACFG;

    ADC1->CR |= ADC_CR_ADEN;
    for (std::uint32_t i = 0; (ADC1->ISR & ADC_ISR_ADRDY) == 0u; ++i) {
        if (i >= kTimeoutLoops) {
            return std::unexpected{Error::AdcNotReady};
        }
    }

    ADC1->CR |= ADC_CR_ADSTART; // далі кожне перетворення починає таймер
    return {};
}

} // namespace

std::expected<void, Error> init() noexcept
{
    if (auto result = clock_init_48mhz(); !result) {
        return result;
    }

    gpio_init();
    pwm_init();
    dma_init();

    if (auto result = adc_init(); !result) {
        return result;
    }

    trigger_timer_init(); // таймер запускаємо останнім: усе вже готове приймати
    return {};
}

void set_duty(std::uint16_t duty) noexcept
{
    TIM3->CCR1 = duty;
}

void panic(Error) noexcept
{
    __disable_irq();
    TIM3->CCR1 = 0u; // навантаження знеструмлено — це головне
    TIM3->CCER &= ~TIM_CCER_CC1E;
    for (;;) {
    }
}

} // namespace board

/// Переривання завершення передачі DMA — єдина точка, звідки виконується
/// конвеєр. Прапорець знімаємо першою дією: інакше вихід із обробника
/// негайно викличе його знову.
extern "C" void DMA1_Channel1_IRQHandler()
{
    if ((DMA1->ISR & DMA_ISR_TCIF1) != 0u) {
        DMA1->IFCR = DMA_IFCR_CTCIF1;
        board::on_sample(g_sample);
    }
}

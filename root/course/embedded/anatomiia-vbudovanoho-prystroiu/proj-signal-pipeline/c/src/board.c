#include "board.h"

#include "stm32g0xx.h" /* заголовок пристрою з CMSIS-пакета STM32CubeG0 */

/* Номер запиту DMAMUX для АЦП на STM32G0 (таблиця запитів DMAMUX
   у довіднику RM0444). Іменованої константи в заголовку пристрою немає. */
#define DMAMUX_REQ_ADC1 5U

#define TIMEOUT_LOOPS 1000000U

/* Комірка, куди DMA кладе черговий відлік. volatile — бо змінює її
   не процесор, а периферія, і компілятор про це знати не може. */
static volatile uint16_t s_adc_sample;

/* ---- Тактування 48 МГц від внутрішнього HSI16 -------------------------- */

static board_status_t clock_init_48mhz(void)
{
    /* 48 МГц — це вже друга смуга затримки Flash, один такт очікування. */
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_0;

    /* PLL від HSI16: M = 1 (поле 0), N = 12, R = 4 (поле 3).
       16 МГц / 1 * 12 = 192 МГц у ГКН, / 4 = 48 МГц на виході R. */
    RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSI
                 | (0U  << RCC_PLLCFGR_PLLM_Pos)
                 | (12U << RCC_PLLCFGR_PLLN_Pos)
                 | (3U  << RCC_PLLCFGR_PLLR_Pos)
                 | RCC_PLLCFGR_PLLREN;

    RCC->CR |= RCC_CR_PLLON;
    for (uint32_t i = 0; (RCC->CR & RCC_CR_PLLRDY) == 0U; ++i) {
        if (i >= TIMEOUT_LOOPS) {
            return BOARD_ERR_PLL_TIMEOUT; /* кварц чи PLL не завелися — далі йти нікуди */
        }
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_1; /* SW = 010: PLLRCLK */
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_1) {
        /* апаратне перемикання джерела, кілька тактів */
    }
    SystemCoreClock = 48000000U;
    return BOARD_OK;
}

/* ---- Ніжки ------------------------------------------------------------- */

static void gpio_init(void)
{
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;

    /* PA0 — аналоговий вхід АЦП (режим 11, він же стан після скидання). */
    GPIOA->MODER |= GPIO_MODER_MODE0;

    /* PA6 — альтернативна функція AF1 = TIM3_CH1 (режим 10). */
    GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODE6) | GPIO_MODER_MODE6_1;
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~GPIO_AFRL_AFSEL6) | (1U << GPIO_AFRL_AFSEL6_Pos);
    GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED6_0; /* середня швидкість фронту, менше дзвону */
}

/* ---- TIM3: ШІМ 16 біт --------------------------------------------------- */

static void pwm_init(void)
{
    RCC->APBENR1 |= RCC_APBENR1_TIM3EN;

    TIM3->PSC = 0U;                 /* 48 МГц / 65536 ≈ 732 Гц несуча */
    TIM3->ARR = 65535U;
    TIM3->CCR1 = 0U;                /* стартуємо з вимкненим навантаженням */

    /* Режим ШІМ 1 (110) із попереднім завантаженням регістра порівняння:
       без OC1PE запис посеред періоду вкоротив би поточний імпульс. */
    TIM3->CCMR1 = TIM_CCMR1_OC1M_2 | TIM_CCMR1_OC1M_1 | TIM_CCMR1_OC1PE;
    TIM3->CCER |= TIM_CCER_CC1E;
    TIM3->CR1 |= TIM_CR1_ARPE;
    TIM3->EGR = TIM_EGR_UG;         /* перенести PSC та ARR у робочі регістри */
    TIM3->CR1 |= TIM_CR1_CEN;
}

/* ---- TIM2: період квантування й запуск АЦП ----------------------------- */

static void trigger_timer_init(void)
{
    RCC->APBENR1 |= RCC_APBENR1_TIM2EN;

    TIM2->PSC = 48U - 1U;                          /* лічильник цокає 1 МГц */
    TIM2->ARR = (1000000U / SAMPLE_PERIOD_HZ) - 1U; /* 10 000 тактів = 10 мс */

    /* MMS = 010: подія оновлення виходить назовні як TRGO.
       Саме звідси береться незмінний dt — а не з викликів у while(1). */
    TIM2->CR2 = TIM_CR2_MMS_1;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->CR1 |= TIM_CR1_CEN;
}

/* ---- DMA: відлік з АЦП у пам'ять без процесора -------------------------- */

static void dma_init(void)
{
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;

    DMAMUX1_Channel0->CCR = DMAMUX_REQ_ADC1; /* канал 1 DMA1 = канал 0 DMAMUX */

    DMA1_Channel1->CPAR = (uint32_t)&ADC1->DR;
    DMA1_Channel1->CMAR = (uint32_t)&s_adc_sample;
    DMA1_Channel1->CNDTR = 1U;

    /* Одна комірка по 16 біт з обох боків, кільцевий режим (лічильник сам
       перезаряджається), переривання завершення передачі. MINC не треба —
       адреса в пам'яті одна й та сама. */
    DMA1_Channel1->CCR = DMA_CCR_PSIZE_0 | DMA_CCR_MSIZE_0
                       | DMA_CCR_CIRC | DMA_CCR_TCIE;
    DMA1_Channel1->CCR |= DMA_CCR_EN;

    /* Найвищий пріоритет: конвеєр мусить відпрацювати до наступного відліку. */
    NVIC_SetPriority(DMA1_Channel1_IRQn, 0);
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);
}

/* ---- АЦП ---------------------------------------------------------------- */

static board_status_t adc_init(void)
{
    RCC->APBENR2 |= RCC_APBENR2_ADCEN;

    /* Тактування перетворювача — PCLK/4 = 12 МГц (CKMODE = 10). */
    ADC1->CFGR2 = ADC_CFGR2_CKMODE_1;

    /* Стабілізатор АЦП: після ввімкнення потрібна пауза (t_ADCVREG_STUP,
       20 мкс за паспортом). На 48 МГц це кількасот тактів. */
    ADC1->CR |= ADC_CR_ADVREGEN;
    for (volatile uint32_t i = 0; i < 2000U; ++i) {
    }

    /* Калібрування — обов'язкове, інакше зсув нуля з'їдає молодші розряди. */
    ADC1->CR |= ADC_CR_ADCAL;
    for (uint32_t i = 0; (ADC1->CR & ADC_CR_ADCAL) != 0U; ++i) {
        if (i >= TIMEOUT_LOOPS) {
            return BOARD_ERR_ADC_CALIBRATION;
        }
    }

    /* Найдовше вікно вибірки (SMP1 = 111, 160.5 такту АЦП). Дільник напруги
       з високим внутрішнім опором інакше не встигає зарядити конденсатор
       вибірки, і виміряна напруга виходить заниженою. */
    ADC1->SMPR = ADC_SMPR_SMP1;
    ADC1->CHSELR = ADC_CHSELR_CHSEL0; /* канал 0 = PA0 */

    /* Зовнішній запуск TRG2 = TIM2_TRGO, фронтом наростання; результат
       їде через DMA у кільцевому режимі. */
    ADC1->CFGR1 = (2U << ADC_CFGR1_EXTSEL_Pos) | ADC_CFGR1_EXTEN_0
                | ADC_CFGR1_DMAEN | ADC_CFGR1_DMACFG;

    ADC1->CR |= ADC_CR_ADEN;
    for (uint32_t i = 0; (ADC1->ISR & ADC_ISR_ADRDY) == 0U; ++i) {
        if (i >= TIMEOUT_LOOPS) {
            return BOARD_ERR_ADC_NOT_READY;
        }
    }

    ADC1->CR |= ADC_CR_ADSTART; /* далі кожне перетворення починає таймер */
    return BOARD_OK;
}

/* ---- Публічний інтерфейс ------------------------------------------------ */

board_status_t board_init(void)
{
    board_status_t status = clock_init_48mhz();
    if (status != BOARD_OK) {
        return status;
    }

    gpio_init();
    pwm_init();
    dma_init();

    status = adc_init();
    if (status != BOARD_OK) {
        return status;
    }

    trigger_timer_init(); /* таймер запускаємо останнім: усе вже готове приймати */
    return BOARD_OK;
}

void board_set_duty(uint16_t duty)
{
    TIM3->CCR1 = duty;
}

void board_panic(board_status_t status)
{
    (void)status;
    __disable_irq();
    TIM3->CCR1 = 0U;            /* навантаження знеструмлено — це головне */
    TIM3->CCER &= ~TIM_CCER_CC1E;
    for (;;) {
    }
}

/* Переривання завершення передачі DMA — єдина точка, звідки виконується
   конвеєр. Прапорець знімаємо першою дією: інакше вихід із обробника
   негайно викличе його знову. */
void DMA1_Channel1_IRQHandler(void)
{
    if ((DMA1->ISR & DMA_ISR_TCIF1) != 0U) {
        DMA1->IFCR = DMA_IFCR_CTCIF1;
        app_on_sample(s_adc_sample);
    }
}

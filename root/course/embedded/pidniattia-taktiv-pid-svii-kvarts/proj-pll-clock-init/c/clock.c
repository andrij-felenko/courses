#include "clock.h"
#include "stm32f4_regs.h"

/* Коефіцієнти контуру для кварцу 8 МГц:
   M=4  -> на вході фазового детектора 2 МГц (дозволено 1..2 МГц)
   N=168 -> VCO 336 МГц (дозволено 100..432 МГц)
   P=2  -> SYSCLK 168 МГц
   Q=7  -> 48 МГц рівно, як просить контролер USB */
#define PLL_M   4UL
#define PLL_N   168UL
#define PLL_P   2UL
#define PLL_Q   7UL

/* Після скидання ядро тактується внутрішнім RC на 16 МГц */
static volatile uint32_t s_sysclk_hz = CLOCK_HSI_HZ;

/* Лічильник аварій CSS не чиститься стартапом: секція .noinit переживає
   програмне скидання, тож після перезапуску видно, що це був зрив кварцу */
__attribute__((section(".noinit"))) static volatile uint32_t s_css_events;

bool clock_wait_masked(volatile uint32_t *reg, uint32_t mask,
                       uint32_t expected, uint32_t cycles)
{
    while ((*reg & mask) != expected) {
        if (cycles-- == 0UL) {
            return false;   /* детермінований вихід замість вічного while */
        }
    }
    return true;
}

uint32_t clock_sysclk_hz(void)
{
    return s_sysclk_hz;
}

void clock_notify_sysclk(uint32_t hz)
{
    s_sysclk_hz = hz;
}

uint32_t clock_css_event_count(void)
{
    return s_css_events;
}

clock_status_t clock_set_flash_latency(uint32_t wait_states)
{
    uint32_t acr = FLASH->ACR & ~FLASH_ACR_LATENCY_MASK;

    acr |= (wait_states << 0) & FLASH_ACR_LATENCY_MASK;
    acr |= FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN;
    FLASH->ACR = acr;

    /* Поле LATENCY читаємо назад: запис приймається не миттєво, і поки він
       не набув чинності, підвищувати частоту не можна */
    if (!clock_wait_masked(&FLASH->ACR, FLASH_ACR_LATENCY_MASK,
                           (wait_states << 0) & FLASH_ACR_LATENCY_MASK,
                           CLOCK_TIMEOUT_CYCLES)) {
        return CLOCK_ERR_FLASH_LATENCY;
    }
    return CLOCK_OK;
}

void clock_reset_flash_caches(void)
{
    /* Біти ICRST/DCRST приймаються лише при вимкнених кешах — інакше запис
       просто ігнорується, а в кеші лишається сміття з попередньої частоти */
    FLASH->ACR &= ~(FLASH_ACR_ICEN | FLASH_ACR_DCEN);
    FLASH->ACR |=  (FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH->ACR &= ~(FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH->ACR |=  (FLASH_ACR_ICEN | FLASH_ACR_DCEN);
}

clock_status_t clock_set_voltage_scale(uint32_t vos_field)
{
    /* Інтерфейс PWR сидить на APB1 і після скидання не тактується */
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    (void)RCC->APB1ENR;   /* холостий читок: запис на APB доходить із затримкою */

    /* VOS дозволено міняти лише при вимкненому PLL — усі виклики нижче це тримають */
    PWR->CR = (PWR->CR & ~PWR_CR_VOS_MASK) | (vos_field & PWR_CR_VOS_MASK);

    /* Регулятор виходить на новий рівень не миттєво; поки VOSRDY внизу,
       кремній ще не витримає максимальної частоти */
    if (!clock_wait_masked(&PWR->CSR, PWR_CSR_VOSRDY, PWR_CSR_VOSRDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        return CLOCK_ERR_VOS_TIMEOUT;
    }
    return CLOCK_OK;
}

void clock_set_bus_prescalers(uint32_t hpre, uint32_t ppre1, uint32_t ppre2)
{
    uint32_t cfgr = RCC->CFGR;

    cfgr &= ~(RCC_CFGR_HPRE_MASK | RCC_CFGR_PPRE1_MASK | RCC_CFGR_PPRE2_MASK);
    cfgr |= hpre | ppre1 | ppre2;
    RCC->CFGR = cfgr;   /* читання-модифікація-запис: інакше стерли б налаштування MCO */
}

void clock_fallback_to_hsi(void)
{
    RCC->CR |= RCC_CR_HSION;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_HSIRDY, RCC_CR_HSIRDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        /* Немає ні кварцу, ні внутрішнього RC — рятувати вже нічим */
        SCB_AIRCR = SCB_AIRCR_SYSRESETREQ;
        for (;;) {
        }
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_MASK) | RCC_CFGR_SW_HSI;
    (void)clock_wait_masked(&RCC->CFGR, RCC_CFGR_SWS_MASK, RCC_CFGR_SWS_HSI,
                            CLOCK_TIMEOUT_CYCLES);

    /* На 16 МГц ділити шини нічим: усе на /1 */
    clock_set_bus_prescalers(RCC_CFGR_HPRE_DIV1, RCC_CFGR_PPRE1_DIV1, RCC_CFGR_PPRE2_DIV1);

    RCC->CR &= ~RCC_CR_PLLON;
    (void)clock_set_flash_latency(CLOCK_FLASH_WS_16MHZ);

    s_sysclk_hz = CLOCK_HSI_HZ;
}

clock_status_t clock_configure_pll168(void)
{
    clock_status_t st;

    /* 1а. Напруга ядра: без Scale 1 кремній на 168 МГц не рахує */
    st = clock_set_voltage_scale(PWR_CR_VOS_SCALE1);
    if (st != CLOCK_OK) {
        clock_fallback_to_hsi();
        return st;
    }

    /* 1б. Затримки Flash піднімаємо ДО частоти: більше тактів очікування
       на 16 МГц лише сповільнює, а менше на 168 МГц дає HardFault */
    st = clock_set_flash_latency(CLOCK_FLASH_WS_168MHZ);
    if (st != CLOCK_OK) {
        clock_fallback_to_hsi();
        return st;
    }

    /* 2. Запуск генератора Пірса на зовнішньому кварці */
    RCC->CR |= RCC_CR_HSEON;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_HSERDY, RCC_CR_HSERDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        RCC->CR &= ~RCC_CR_HSEON;   /* не тримаємо ввімкненим мертвий генератор */
        clock_fallback_to_hsi();
        return CLOCK_ERR_HSE_TIMEOUT;
    }

    /* 3. Переддільники шин виставляємо до перемикання: APB1 має ліміт 45 МГц,
       APB2 — 90 МГц, і на 168 МГц із дільником /1 вони б згоріли за таймінгами */
    clock_set_bus_prescalers(RCC_CFGR_HPRE_DIV1, RCC_CFGR_PPRE1_DIV4, RCC_CFGR_PPRE2_DIV2);

    /* 4. Коефіцієнти PLL пишуться лише при вимкненому контурі */
    RCC->CR &= ~RCC_CR_PLLON;
    (void)clock_wait_masked(&RCC->CR, RCC_CR_PLLRDY, 0UL, CLOCK_TIMEOUT_CYCLES);
    RCC->PLLCFGR = (PLL_M << RCC_PLLCFGR_PLLM_SHIFT)
                 | (PLL_N << RCC_PLLCFGR_PLLN_SHIFT)
                 | (((PLL_P / 2UL) - 1UL) << RCC_PLLCFGR_PLLP_SHIFT)
                 | RCC_PLLCFGR_PLLSRC_HSE
                 | (PLL_Q << RCC_PLLCFGR_PLLQ_SHIFT);

    /* 5. Запуск контуру й очікування фазового захоплення */
    RCC->CR |= RCC_CR_PLLON;
    if (!clock_wait_masked(&RCC->CR, RCC_CR_PLLRDY, RCC_CR_PLLRDY,
                           CLOCK_TIMEOUT_CYCLES)) {
        RCC->CR &= ~RCC_CR_PLLON;
        clock_fallback_to_hsi();
        return CLOCK_ERR_PLL_TIMEOUT;
    }

    /* 6. Перемикання системного мультиплексора й підтвердження від апаратури */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_MASK) | RCC_CFGR_SW_PLL;
    if (!clock_wait_masked(&RCC->CFGR, RCC_CFGR_SWS_MASK, RCC_CFGR_SWS_PLL,
                           CLOCK_TIMEOUT_CYCLES)) {
        clock_fallback_to_hsi();
        return CLOCK_ERR_SWITCH_TIMEOUT;
    }

    /* 7. Тепер, коли кварц справді тримає систему, вмикаємо його апаратний монітор */
    RCC->CR |= RCC_CR_CSSON;

    s_sysclk_hz = CLOCK_PLL_HZ;
    return CLOCK_OK;
}

/* Аварійне гасіння силової частини: MOE=0 одним записом знімає всі виходи
   ШІМ мосту, тож мотор не лишиться під напругою на невідомій частоті */
static void css_force_safe_state(void)
{
    TIM1_BDTR &= ~TIM_BDTR_MOE;
}

/* Немасковане переривання: єдиний його штатний привід тут — зрив кварцу */
void NMI_Handler(void)
{
    if ((RCC->CIR & RCC_CIR_CSSF) == 0UL) {
        /* NMI не від CSS: причина невідома, безпечніше перезапуститись */
        SCB_AIRCR = SCB_AIRCR_SYSRESETREQ;
        for (;;) {
        }
    }

    /* Апаратний автомат RCC уже сам перемкнув SYSCLK на HSI і вимкнув PLL,
       тож цей код виконується на 16 МГц із затримками Flash на 5 WS —
       зайві такти очікування безпечні, зменшувати їх тут нічого не дає */
    css_force_safe_state();

    RCC->CIR |= RCC_CIR_CSSC;     /* запис 1 у CSSC знімає прапорець CSSF */
    RCC->CR  &= ~RCC_CR_HSEON;    /* знімаємо і дозвіл мертвого генератора */

    s_sysclk_hz = CLOCK_HSI_HZ;
    s_css_events++;               /* причина аварії переживе перезапуск */

    for (;;) {
        /* чекаємо на скидання від сторожового таймера: перезапуск із чистого
           стану надійніший за спробу жити далі на невідомому тактуванні */
    }
}

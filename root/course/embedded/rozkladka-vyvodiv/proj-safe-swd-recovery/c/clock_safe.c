#include "clock_safe.h"

#include "stm32f4xx.h"

#include <stdbool.h>

#define HSE_HZ  8000000UL
#define HSI_HZ  16000000UL

/* Скільки порожніх обертів чекаємо на кожен апаратний прапорець готовності. */
#define WAIT_LOOPS  200000UL

typedef struct {
    uint32_t m;   /* дільник входу VCO       */
    uint32_t n;   /* множник VCO             */
    uint32_t p;   /* дільник виходу на SYSCLK */
    uint32_t q;   /* дільник виходу на USB    */
} pll_t;

/* Обидва набори дають на вході VCO рівно 1 МГц і 168 МГц на виході. */
static const pll_t PLL_FROM_HSE = { .m = 8U,  .n = 336U, .p = 2U, .q = 7U };
static const pll_t PLL_FROM_HSI = { .m = 16U, .n = 336U, .p = 2U, .q = 7U };

static uint32_t s_sysclk_hz = HSI_HZ;

static bool pll_is_valid(const pll_t *pll, uint32_t src_hz, uint32_t *out_hz)
{
    if ((pll->m < 2U) || (pll->m > 63U) ||
        (pll->n < 50U) || (pll->n > 432U) ||
        ((pll->p != 2U) && (pll->p != 4U) && (pll->p != 6U) && (pll->p != 8U)) ||
        (pll->q < 2U) || (pll->q > 15U)) {
        return false;
    }

    const uint32_t vco_in  = src_hz / pll->m;
    const uint32_t vco_out = vco_in * pll->n;
    const uint32_t sysclk  = vco_out / pll->p;

    /* Межі з документації: вхід VCO 1..2 МГц, вихід 100..432 МГц, ядро ≤ 168 МГц. */
    if ((vco_in < 1000000UL) || (vco_in > 2000000UL)) {
        return false;
    }
    if ((vco_out < 100000000UL) || (vco_out > 432000000UL)) {
        return false;
    }
    if (sysclk > 168000000UL) {
        return false;
    }

    *out_hz = sysclk;
    return true;
}

/* Очікування прапорця з обмеженням; false означає «не дочекалися». */
static bool wait_flag(volatile const uint32_t *reg, uint32_t mask, bool expect_set)
{
    for (uint32_t i = 0; i < WAIT_LOOPS; ++i) {
        const bool is_set = (*reg & mask) != 0U;
        if (is_set == expect_set) {
            return true;
        }
    }
    return false;
}

static bool set_flash_latency(uint32_t wait_states)
{
    uint32_t acr = FLASH->ACR;

    acr &= ~FLASH_ACR_LATENCY;
    acr |= (wait_states & FLASH_ACR_LATENCY) | FLASH_ACR_PRFTEN
         | FLASH_ACR_ICEN | FLASH_ACR_DCEN;
    FLASH->ACR = acr;

    /* Затримку читання підтверджуємо зворотним читанням: інакше ядро зависне на першій же вибірці. */
    return (FLASH->ACR & FLASH_ACR_LATENCY) == (wait_states & FLASH_ACR_LATENCY);
}

/* Гарантований відкат: ядро на HSI 16 МГц, нульова затримка Flash, PLL вимкнено. */
static clock_state_t fallback_to_hsi(clock_status_t status)
{
    RCC->CR |= RCC_CR_HSION;
    (void)wait_flag(&RCC->CR, RCC_CR_HSIRDY, true);

    RCC->CFGR &= ~RCC_CFGR_SW;                       /* SYSCLK = HSI */
    (void)wait_flag(&RCC->CFGR, RCC_CFGR_SWS, false);

    RCC->CR &= ~RCC_CR_PLLON;
    (void)wait_flag(&RCC->CR, RCC_CR_PLLRDY, false);

    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    (void)set_flash_latency(0U);

    s_sysclk_hz = HSI_HZ;
    SystemCoreClock = HSI_HZ;

    clock_state_t state = { .source = CLOCK_SRC_HSI, .sysclk_hz = HSI_HZ, .status = status };
    return state;
}

clock_state_t clock_safe_init(void)
{
    /* 1. Спочатку сідаємо на HSI: усі подальші дії робимо з відомого стану. */
    RCC->CR |= RCC_CR_HSION;
    if (!wait_flag(&RCC->CR, RCC_CR_HSIRDY, true)) {
        /* HSI не вмикається — сподіватися більше нема на що, лишаємось як є. */
        clock_state_t dead = { CLOCK_SRC_HSI, HSI_HZ, CLOCK_ERR_SWITCH_TIMEOUT };
        return dead;
    }
    RCC->CFGR &= ~RCC_CFGR_SW;
    (void)wait_flag(&RCC->CFGR, RCC_CFGR_SWS, false);

    RCC->CR &= ~RCC_CR_PLLON;
    (void)wait_flag(&RCC->CR, RCC_CR_PLLRDY, false);

    /* 2. Пробуємо зовнішній кварц. Не завівся — це не привід зависати. */
    clock_status_t status = CLOCK_OK;
    bool from_hse = true;

    RCC->CR |= RCC_CR_HSEON;
    if (!wait_flag(&RCC->CR, RCC_CR_HSERDY, true)) {
        RCC->CR &= ~RCC_CR_HSEON;
        from_hse = false;
        status = CLOCK_ERR_HSE_TIMEOUT;
    }

    const pll_t *pll = from_hse ? &PLL_FROM_HSE : &PLL_FROM_HSI;
    const uint32_t src_hz = from_hse ? HSE_HZ : HSI_HZ;

    uint32_t target_hz = 0U;
    if (!pll_is_valid(pll, src_hz, &target_hz)) {
        return fallback_to_hsi(CLOCK_ERR_BAD_PLL);
    }

    /* 3. Живлення й затримка Flash — до підняття частоти, а не після. */
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    (void)RCC->APB1ENR;
    PWR->CR |= PWR_CR_VOS;                 /* режим напруги 1: дозволяє 168 МГц */

    if (!set_flash_latency(FLASH_ACR_LATENCY_5WS)) {
        return fallback_to_hsi(CLOCK_ERR_SWITCH_TIMEOUT);
    }

    /* 4. Дільники шин: AHB 168, APB1 42, APB2 84 МГц. */
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CFGR |= RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    RCC->PLLCFGR = (pll->m << 0U)
                 | (pll->n << 6U)
                 | (((pll->p / 2U) - 1U) << 16U)
                 | (pll->q << 24U)
                 | (from_hse ? RCC_PLLCFGR_PLLSRC_HSE : 0U);

    /* 5. Захоплення PLL з обмеженим очікуванням. */
    RCC->CR |= RCC_CR_PLLON;
    if (!wait_flag(&RCC->CR, RCC_CR_PLLRDY, true)) {
        return fallback_to_hsi(CLOCK_ERR_PLL_TIMEOUT);
    }

    /* 6. Перемикання SYSCLK; поле SWS має підтвердити перехід. */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    for (uint32_t i = 0; i < WAIT_LOOPS; ++i) {
        if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
            s_sysclk_hz = target_hz;
            SystemCoreClock = target_hz;

            clock_state_t state = {
                .source    = from_hse ? CLOCK_SRC_HSE_PLL : CLOCK_SRC_HSI_PLL,
                .sysclk_hz = target_hz,
                .status    = status
            };
            return state;
        }
    }
    return fallback_to_hsi(CLOCK_ERR_SWITCH_TIMEOUT);
}

uint32_t clock_safe_sysclk_hz(void)
{
    return s_sysclk_hz;
}

void clock_safe_delay_ms(uint32_t ms)
{
    const uint32_t ticks = s_sysclk_hz / 1000U;

    if ((ticks == 0U) || (ticks > SysTick_LOAD_RELOAD_Msk)) {
        return;   /* частота поза межами лічильника — краще нічого, ніж вічний цикл */
    }

    SysTick->LOAD = ticks - 1U;
    SysTick->VAL  = 0U;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;

    while (ms-- > 0U) {
        while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk) == 0U) {
        }
    }
    SysTick->CTRL = 0U;
}

const char *clock_status_str(clock_status_t status)
{
    switch (status) {
    case CLOCK_OK:                 return "ok";
    case CLOCK_ERR_HSE_TIMEOUT:    return "кварц не завівся";
    case CLOCK_ERR_PLL_TIMEOUT:    return "PLL не захопився";
    case CLOCK_ERR_SWITCH_TIMEOUT: return "перемикач SYSCLK не відповів";
    case CLOCK_ERR_BAD_PLL:        return "коефіцієнти PLL поза межами";
    default:                       return "невідомий стан";
    }
}

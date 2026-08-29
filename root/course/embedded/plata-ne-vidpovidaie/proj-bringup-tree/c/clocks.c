/* Фаза 1: верифікація тактових доменів.
   Головне правило цього файла — жодного очікування без лічильника. Прошивка,
   яка перевіряє кварц, не має права зависнути на кварці, якого немає. */
#include "bringup.h"
#include "stm32f4_regs.h"

/* HSE 8 МГц → VCO 336 МГц → SYSCLK 168 МГц (M=8, N=336, P=2, Q=7).
   Ми лише переконуємося, що петля захоплюється, і гасимо її назад. */
#define PLL_M 8U
#define PLL_N 336U
#define PLL_P 2U
#define PLL_Q 7U

/* Приблизні межі очікування при 16 МГц: 200000 ітерацій ≈ 50 мс,
   що з великим запасом перекриває час розгойдування кварцу (типово 2–5 мс). */
#define HSI_TRIES  10000U
#define HSE_TRIES 200000U
#define PLL_TRIES  50000U

static bool wait_flag(volatile uint32_t *reg, uint32_t mask, bool want_set, uint32_t tries)
{
    while (tries > 0U) {
        bool now = (*reg & mask) != 0U;
        if (now == want_set) {
            return true;
        }
        --tries;
    }
    return false;
}

bringup_status_t bringup_clock_check(bringup_report_t *report)
{
    /* HSI — єдине джерело, яке не залежить від жодного зовнішнього компонента.
       Якщо не готове воно, справа не в платі, а в самому кристалі. */
    RCC_CR |= RCC_CR_HSION;
    report->hsi_ready = wait_flag(&RCC_CR, RCC_CR_HSIRDY, true, HSI_TRIES);

    /* Явно тримаємося HSI: SW = 00, чекаємо підтвердження в SWS. */
    RCC_CFGR &= ~RCC_CFGR_SW_MASK;
    (void)wait_flag(&RCC_CFGR, RCC_CFGR_SWS_MASK, false, HSI_TRIES);

    /* Запуск кварцу. Найчастіший дефект тут — невдалі C1/C2: інвертор не
       перекриває втрати кристала, HSERDY не встає ніколи. */
    RCC_CR |= RCC_CR_HSEON;
    report->hse_ready = wait_flag(&RCC_CR, RCC_CR_HSERDY, true, HSE_TRIES);
    if (!report->hse_ready) {
        /* Гасимо драйвер: тримати ввімкненим генератор, який не заводиться,
           немає сенсу — це лише зайвий струм і нагрів. */
        RCC_CR &= ~RCC_CR_HSEON;
        report->clock_status = BRINGUP_ERR_HSE_TIMEOUT;
        return BRINGUP_ERR_HSE_TIMEOUT;
    }

    /* PLLCFGR дозволено чіпати лише при вимкненій петлі. */
    RCC_CR &= ~RCC_CR_PLLON;
    (void)wait_flag(&RCC_CR, RCC_CR_PLLRDY, false, PLL_TRIES);

    RCC_PLLCFGR = (PLL_M << 0)
                | (PLL_N << 6)
                | (((PLL_P / 2U) - 1U) << 16)
                | RCC_PLLCFGR_SRC_HSE
                | (PLL_Q << 24);

    RCC_CR |= RCC_CR_PLLON;
    report->pll_ready = wait_flag(&RCC_CR, RCC_CR_PLLRDY, true, PLL_TRIES);
    if (!report->pll_ready) {
        RCC_CR &= ~RCC_CR_PLLON;
        report->clock_status = BRINGUP_ERR_PLL_TIMEOUT;
        return BRINGUP_ERR_PLL_TIMEOUT;
    }

    /* Захоплення є — цього досить. Гасимо PLL і лишаємося на HSI: решта
       перевірок має йти на джерелі, у якому ми вже впевнені. */
    RCC_CR &= ~RCC_CR_PLLON;
    report->clock_status = BRINGUP_OK;
    return BRINGUP_OK;
}

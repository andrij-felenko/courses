#include "rtc_wakeup.h"
#include "stm32l4xx.h"

/* LSE 32768 Гц: PREDIV_A=31, PREDIV_S=1023 дають ck_spre 1 Гц і крок SSR ≈ 1 мс. */
#define PREDIV_A     31u
#define PREDIV_S     1023u
/* Джерело WUT — RTCCLK/16 = 2048 Гц (WUCKSEL = 000). */
#define WUT_HZ       2048u
#define HOUR_MS      3600000u
#define RTC_SPINS    100000u

static uint32_t s_armed_at_ms;
static volatile bool s_expired;

static void wpr_unlock(void)
{
    RTC->WPR = 0xCAu;
    RTC->WPR = 0x53u;
}

static void wpr_lock(void)
{
    RTC->WPR = 0xFFu;
}

static bool spin_until_set(volatile uint32_t *reg, uint32_t mask)
{
    for (uint32_t i = 0; i < RTC_SPINS; ++i) {
        if ((*reg & mask) != 0u) {
            return true;
        }
    }
    return false;
}

static uint32_t bcd_to_bin(uint32_t bcd)
{
    return ((bcd >> 4) & 0xFu) * 10u + (bcd & 0xFu);
}

/* Час у межах години в мілісекундах. Для сну до 32 с цього досить,
 * а перехід через годину знімається відніманням за модулем. */
static uint32_t rtc_now_ms(void)
{
    uint32_t ssr, tr, ssr_again;
    do {
        ssr = RTC->SSR;
        tr  = RTC->TR;
        ssr_again = RTC->SSR;
    } while (ssr != ssr_again); /* захист від зміни секунди між читаннями */

    uint32_t sec = bcd_to_bin((tr & (RTC_TR_ST | RTC_TR_SU)) >> RTC_TR_SU_Pos);
    uint32_t min = bcd_to_bin((tr & (RTC_TR_MNT | RTC_TR_MNU)) >> RTC_TR_MNU_Pos);
    /* SSR рахує ВНИЗ від PREDIV_S */
    uint32_t frac = ((PREDIV_S - ssr) * 1000u) / (PREDIV_S + 1u);
    return (min * 60u + sec) * 1000u + frac;
}

void rtc_wakeup_init(void)
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN | RCC_APB1ENR1_RTCAPBEN;
    PWR->CR1 |= PWR_CR1_DBP; /* домен резервного живлення відкрито на запис */

    if ((RCC->BDCR & RCC_BDCR_RTCEN) == 0u) {
        RCC->BDCR |= RCC_BDCR_LSEON;
        if (!spin_until_set(&RCC->BDCR, RCC_BDCR_LSERDY)) {
            /* Без годинникового кварцу глибокий сон за часом неможливий:
             * система житиме на перериваннях периферії. */
            return;
        }
        RCC->BDCR = (RCC->BDCR & ~RCC_BDCR_RTCSEL) | RCC_BDCR_RTCSEL_0; /* LSE */
        RCC->BDCR |= RCC_BDCR_RTCEN;

        wpr_unlock();
        RTC->ISR = RTC_ISR_INIT;
        (void)spin_until_set(&RTC->ISR, RTC_ISR_INITF);
        RTC->PRER = (PREDIV_A << RTC_PRER_PREDIV_A_Pos) | PREDIV_S;
        RTC->CR  |= RTC_CR_BYPSHAD; /* читаємо лічильники напряму, без тіней */
        RTC->ISR &= ~RTC_ISR_INIT;
        wpr_lock();
    }

    /* Пробудження ядра з STOP іде через лінію подій 20. */
    EXTI->IMR1  |= EXTI_IMR1_IM20;
    EXTI->RTSR1 |= EXTI_RTSR1_RT20;
    NVIC_SetPriority(RTC_WKUP_IRQn, 3);
    NVIC_EnableIRQ(RTC_WKUP_IRQn);
}

uint32_t rtc_wakeup_arm(uint32_t ms)
{
    if (ms > RTC_WAKEUP_MAX_MS) {
        ms = RTC_WAKEUP_MAX_MS;
    }
    uint32_t counts = (ms * WUT_HZ) / 1000u;
    if (counts == 0u) {
        counts = 1u;
    }

    wpr_unlock();
    RTC->CR &= ~(RTC_CR_WUTE | RTC_CR_WUTIE);
    if (!spin_until_set(&RTC->ISR, RTC_ISR_WUTWF)) {
        wpr_lock();
        return 0u; /* таймер не дався на перезапис — засинаємо без будильника */
    }
    RTC->CR  &= ~RTC_CR_WUCKSEL;         /* RTCCLK/16 */
    RTC->WUTR = counts - 1u;             /* лічильник вистрелює на переході через нуль */
    RTC->ISR &= ~RTC_ISR_WUTF;
    EXTI->PR1 = EXTI_PR1_PIF20;
    RTC->CR  |= RTC_CR_WUTE | RTC_CR_WUTIE;
    wpr_lock();

    s_expired = false;
    s_armed_at_ms = rtc_now_ms();
    return (counts * 1000u) / WUT_HZ;
}

void rtc_wakeup_disarm(void)
{
    wpr_unlock();
    RTC->CR &= ~(RTC_CR_WUTE | RTC_CR_WUTIE);
    RTC->ISR &= ~RTC_ISR_WUTF;
    wpr_lock();
    EXTI->PR1 = EXTI_PR1_PIF20;
}

uint32_t rtc_wakeup_elapsed_ms(void)
{
    uint32_t now = rtc_now_ms();
    return (now + HOUR_MS - s_armed_at_ms) % HOUR_MS;
}

bool rtc_wakeup_expired(void)
{
    return s_expired;
}

void RTC_WKUP_IRQHandler(void)
{
    if ((RTC->ISR & RTC_ISR_WUTF) != 0u) {
        RTC->ISR &= ~RTC_ISR_WUTF; /* прапорці RTC скидаються записом нуля */
        s_expired = true;
    }
    EXTI->PR1 = EXTI_PR1_PIF20;
}

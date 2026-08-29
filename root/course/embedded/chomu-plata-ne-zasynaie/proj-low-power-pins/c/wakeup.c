#include "wakeup.h"

#define WAKE_BUTTON_PIN 0U      /* PA0 */
#define EXTI_LINE_BUTTON (1UL << 0)
#define EXTI_LINE_RTC_WKUP (1UL << 20) /* лінія 20 — будильник RTC */

static volatile wake_reason_t g_reason;

const char *wake_reason_str(wake_reason_t r)
{
    switch (r) {
    case WAKE_BUTTON: return "кнопка";
    case WAKE_RTC:    return "будильник RTC";
    default:          return "невідомо";
    }
}

wake_reason_t wakeup_last_reason(void)
{
    return g_reason;
}

/* Знімає захист від запису в регістри RTC. Ключі задані в даташиті. */
static void rtc_unlock(void)
{
    RTC->WPR = 0xCAU;
    RTC->WPR = 0x53U;
}

static void rtc_lock(void)
{
    RTC->WPR = 0xFFU;
}

static void rtc_clock_init(void)
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN | RCC_APB1ENR1_RTCAPB;
    PWR->CR1 |= PWR_CR1_DBP; /* без цього біта домен RTC не пускає запис */

    if ((RCC->BDCR & RCC_BDCR_RTCEN) != 0U) {
        return; /* RTC уже йде — переінакшувати його означало б збити час */
    }

    RCC->BDCR |= RCC_BDCR_LSEON;
    /* Годинниковий кварц заводиться повільно — сотні мілісекунд. */
    for (uint32_t left = 2000U; left != 0U; left--) {
        if ((RCC->BDCR & RCC_BDCR_LSERDY) != 0U) {
            break;
        }
        mcu_delay_ms(1U);
    }

    RCC->BDCR |= RCC_BDCR_RTCSEL_LSE | RCC_BDCR_RTCEN;
}

void wakeup_init(void)
{
    /* --- кнопка на PA0 --- */
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;
    SYSCFG->EXTICR[0] &= ~0xFUL;  /* лінію EXTI0 бере порт A (код 0) */

    gpio_mode(GPIOA, WAKE_BUTTON_PIN, MODE_INPUT);
    /* Кнопка замикає на землю, тому підтяжка вгору потрібна. Це та сама
     * підтяжка, що потім тягне струм увесь сон, — 40 кОм на 3.3 В дають
     * 82 мкА, поки кнопку тримають натиснутою. Ціна за живий вхід. */
    gpio_pull(GPIOA, WAKE_BUTTON_PIN, PULL_UP);

    EXTI->FTSR1 |= EXTI_LINE_BUTTON;  /* натискання — це спадний фронт */
    EXTI->PR1 = EXTI_LINE_BUTTON;
    EXTI->IMR1 |= EXTI_LINE_BUTTON;
    nvic_clear_pending(IRQ_EXTI0);
    nvic_enable(IRQ_EXTI0);

    /* --- будильник RTC --- */
    rtc_clock_init();

    EXTI->RTSR1 |= EXTI_LINE_RTC_WKUP;
    EXTI->PR1 = EXTI_LINE_RTC_WKUP;
    EXTI->IMR1 |= EXTI_LINE_RTC_WKUP;
    nvic_clear_pending(IRQ_RTC_WKUP);
    nvic_enable(IRQ_RTC_WKUP);
}

void wakeup_arm_rtc(uint16_t seconds)
{
    rtc_unlock();

    RTC->CR &= ~RTC_CR_WUTE;
    /* Лічильник можна переписувати лише тоді, коли залізо це дозволило. */
    for (uint32_t left = 1000U; left != 0U; left--) {
        if ((RTC->ISR & RTC_ISR_WUTWF) != 0U) {
            break;
        }
        mcu_delay_us(100U);
    }

    RTC->WUTR = (seconds > 0U) ? (uint32_t)(seconds - 1U) : 0U;
    RTC->CR = (RTC->CR & ~0x7UL) | RTC_CR_WUCKSEL_1HZ;
    RTC->ISR &= ~RTC_ISR_WUTF;
    RTC->CR |= RTC_CR_WUTE | RTC_CR_WUTIE;

    rtc_lock();
}

void wakeup_clear_pending(void)
{
    /* Черга переривань мусить бути порожня в момент WFI. Незнятий прапорець
     * будить ядро тієї ж миті, і зовні це виглядає так, ніби плата взагалі
     * не засинає: споживання лишається робочим, а програма крутиться. */
    rtc_unlock();
    RTC->ISR &= ~RTC_ISR_WUTF;
    rtc_lock();

    EXTI->PR1 = EXTI_LINE_BUTTON | EXTI_LINE_RTC_WKUP;

    nvic_clear_pending(IRQ_EXTI0);
    nvic_clear_pending(IRQ_RTC_WKUP);

    g_reason = WAKE_NONE;
}

/* Обробники лише знімають прапорці й називають причину: усе інше робиться в
 * головному циклі, куди ядро повертається одразу після WFI. */
void EXTI0_IRQHandler(void)
{
    EXTI->PR1 = EXTI_LINE_BUTTON;
    g_reason = WAKE_BUTTON;
}

void RTC_WKUP_IRQHandler(void)
{
    rtc_unlock();
    RTC->ISR &= ~RTC_ISR_WUTF;
    rtc_lock();

    EXTI->PR1 = EXTI_LINE_RTC_WKUP;
    g_reason = WAKE_RTC;
}

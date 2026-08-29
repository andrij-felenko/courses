#include "lowpower.h"
#include "debugctl.h"
#include "i2c.h"
#include "pins.h"
#include "regs.h"

static sleep_stage_t s_stage = SLEEP_STAGE_AWAKE;
static wake_source_t s_wake  = WAKE_UNKNOWN;
static uint32_t s_float_a, s_float_b, s_float_c;

sleep_stage_t lowpower_stage(void)          { return s_stage; }
wake_source_t lowpower_last_wake_source(void) { return s_wake; }
uint32_t lowpower_floating_mask_b(void)     { return s_float_b; }

/* ---------- RTC: єдине джерело часу, що переживає Stop2 ---------- */

static void rtc_unlock(void)  { RTC_WPR = 0xCA; RTC_WPR = 0x53; }
static void rtc_lock(void)    { RTC_WPR = 0xFF; }

sleep_err_t lowpower_rtc_init(void)
{
    PWR_CR1 |= PWR_CR1_DBP;             /* доступ до домену резервного живлення */

    if ((RCC_BDCR & RCC_BDCR_LSERDY) == 0u) {
        RCC_BDCR |= RCC_BDCR_LSEON;
        for (uint32_t spin = 0; spin < 2000000u; ++spin) {
            if (RCC_BDCR & RCC_BDCR_LSERDY) {
                break;
            }
        }
        if ((RCC_BDCR & RCC_BDCR_LSERDY) == 0u) {
            return SLEEP_ERR_RTC_TIMEOUT; /* кварц 32 кГц не завівся */
        }
    }

    if ((RCC_BDCR & RCC_BDCR_RTCEN) == 0u) {
        RCC_BDCR |= RCC_BDCR_RTCSEL_LSE | RCC_BDCR_RTCEN;
    }

    /* Лінія EXTI таймера пробудження мусить бути дозволена, інакше подія
     * не витягне ядро зі Stop2. */
    EXTI_RTSR1 |= EXTI_LINE_RTC_WAKEUP;
    EXTI_IMR1  |= EXTI_LINE_RTC_WAKEUP;
    NVIC_ISER0  = (1u << IRQ_RTC_WKUP);
    return SLEEP_OK;
}

static sleep_err_t rtc_arm_wakeup(uint32_t seconds)
{
    rtc_unlock();
    RTC_CR &= ~RTC_CR_WUTE;

    /* Таймер приймає нове значення лише коли сам його відпустив. */
    sleep_err_t err = SLEEP_ERR_RTC_TIMEOUT;
    for (uint32_t spin = 0; spin < 200000u; ++spin) {
        if (RTC_ISR & RTC_ISR_WUTWF) {
            err = SLEEP_OK;
            break;
        }
    }
    if (err != SLEEP_OK) {
        rtc_lock();
        return err;
    }

    RTC_WUTR = seconds - 1u;                 /* такт 1 Гц */
    RTC_CR = (RTC_CR & ~7u) | RTC_CR_WUCKSEL_SPRE | RTC_CR_WUTE | RTC_CR_WUTIE;
    RTC_ISR &= ~RTC_ISR_WUTF;
    rtc_lock();

    EXTI_PR1 = EXTI_LINE_RTC_WAKEUP;         /* залишки попередньої події */
    NVIC_ICPR0 = (1u << IRQ_RTC_WKUP);
    return SLEEP_OK;
}

static void rtc_disarm_wakeup(void)
{
    rtc_unlock();
    RTC_CR &= ~RTC_CR_WUTE;
    RTC_ISR &= ~RTC_ISR_WUTF;
    rtc_lock();
    EXTI_PR1 = EXTI_LINE_RTC_WAKEUP;
}

/* ---------- кроки автомата ---------- */

/* Крок 1. Периферія стихає, лінії комутованого домену йдуть у нуль,
 * поки шина датчика ще під напругою. */
static void stage_park_buses(void)
{
    i2c1_deinit();
    board_park_switched_domain();
    s_stage = SLEEP_STAGE_BUSES_PARKED;
}

/* Крок 2. Ключ розмикається, і ми перевіряємо, що шина справді просіла.
 * Жива шина при розімкненому ключі — це фантомне живлення через ESD-діод. */
static sleep_err_t stage_rail_off(void)
{
    if (s_stage != SLEEP_STAGE_BUSES_PARKED) {
        return SLEEP_ERR_SEQUENCE;
    }
    board_rail_off();
    s_stage = SLEEP_STAGE_RAIL_OFF;
    return board_rail_is_discharged() ? SLEEP_OK : SLEEP_ERR_RAIL_POWERED;
}

/* Крок 3. Усе, що не має ролі, втрачає цифровий буфер. */
static sleep_err_t stage_pins_analog(void)
{
    if (s_stage != SLEEP_STAGE_RAIL_OFF) {
        return SLEEP_ERR_SEQUENCE;
    }
    board_pins_to_analog();
    s_stage = SLEEP_STAGE_PINS_ANALOG;
    return SLEEP_OK;
}

/* Крок 4. Блок налагодження перестає тримати генератори. */
static sleep_err_t stage_debug_silent(void)
{
    if (s_stage != SLEEP_STAGE_PINS_ANALOG) {
        return SLEEP_ERR_SEQUENCE;
    }
    const bool probe = debug_probe_attached();
    debug_silence_core();
    debug_unfreeze_peripherals();
    debug_low_power_supervisors();
    s_stage = SLEEP_STAGE_DEBUG_SILENT;
    return probe ? SLEEP_ERR_PROBE_ATTACHED : SLEEP_OK;
}

/* Крок 5. Озброюємо пробудження: таймер RTC і кнопка на WKUP1. */
static sleep_err_t stage_arm_wake(uint32_t seconds)
{
    if (s_stage != SLEEP_STAGE_DEBUG_SILENT) {
        return SLEEP_ERR_SEQUENCE;
    }
    /* seconds == 0 — свідомий випадок: годинника немає (не завівся LSE),
     * і єдиним джерелом пробудження лишається кнопка на WKUP1. */
    if (seconds > 0u) {
        const sleep_err_t err = rtc_arm_wakeup(seconds);
        if (err != SLEEP_OK) {
            return err;
        }
    }
    PWR_SCR = PWR_SCR_CWUF_ALL;
    PWR_CR4 |= PWR_CR4_WP1;      /* кнопка замикає на землю: спад */
    PWR_CR3 |= PWR_CR3_EWUP1;
    s_stage = SLEEP_STAGE_WAKE_ARMED;
    return SLEEP_OK;
}

/* Крок 6. Останній огляд перед WFI: жодного цифрового входу без підтяжки. */
static sleep_err_t stage_audit(void)
{
    if (s_stage != SLEEP_STAGE_WAKE_ARMED) {
        return SLEEP_ERR_SEQUENCE;
    }
    if ((RTC_CR & RTC_CR_WUTE) == 0u && (PWR_CR3 & PWR_CR3_EWUP1) == 0u) {
        return SLEEP_ERR_NO_WAKE_SOURCE;
    }
    if (board_audit_floating(&s_float_a, &s_float_b, &s_float_c) != 0u) {
        return SLEEP_ERR_FLOATING_PINS;
    }
    s_stage = SLEEP_STAGE_READY;
    return SLEEP_OK;
}

static void enter_wfi(uint32_t lpms)
{
    PWR_CR1 = (PWR_CR1 & ~PWR_CR1_LPMS_MASK) | lpms;
    SCB_SCR |= SCB_SCR_SLEEPDEEP;
    __asm volatile("dsb");
    __asm volatile("wfi");
    __asm volatile("isb");
    SCB_SCR &= ~SCB_SCR_SLEEPDEEP;
}

static void note_wake_source(void)
{
    if (PWR_SR1 & PWR_SR1_WUF1) {
        s_wake = WAKE_BUTTON;
    } else if (RTC_ISR & RTC_ISR_WUTF) {
        s_wake = WAKE_RTC;
    } else {
        s_wake = WAKE_UNKNOWN;   /* сторонній EXTI: наводка на лінію пробудження */
    }
    PWR_SCR = PWR_SCR_CWUF_ALL;
    rtc_disarm_wakeup();
}

/* ---------- публічні точки входу ---------- */

sleep_err_t lowpower_enter_stop2(uint32_t seconds)
{
    sleep_err_t soft = SLEEP_OK;

    s_stage = SLEEP_STAGE_AWAKE;
    stage_park_buses();

    sleep_err_t err = stage_rail_off();
    if (err == SLEEP_ERR_RAIL_POWERED) {
        /* Одна спроба: часто досить довше потримати лінії в нулі, щоб
         * ємності знеструмленого вузла розрядилися через власне навантаження. */
        board_delay_ms(10);
        if (!board_rail_is_discharged()) {
            soft = SLEEP_ERR_RAIL_POWERED;   /* дефект плати, але спати треба */
        }
    } else if (err != SLEEP_OK) {
        return err;
    }

    err = stage_pins_analog();
    if (err != SLEEP_OK) {
        return err;
    }

    err = stage_debug_silent();
    if (err == SLEEP_ERR_PROBE_ATTACHED) {
        soft = SLEEP_ERR_PROBE_ATTACHED;
    } else if (err != SLEEP_OK) {
        return err;
    }

    err = stage_arm_wake(seconds);
    if (err != SLEEP_OK) {
        return err;
    }

    err = stage_audit();
    if (err != SLEEP_OK) {
        /* Плаваючі виводи — це сотні мікроампер на пін. Замість того щоб
         * заснути з витоком, приводимо їх у порядок і перевіряємо ще раз. */
        board_pins_to_analog();
        s_stage = SLEEP_STAGE_WAKE_ARMED;
        if (stage_audit() != SLEEP_OK) {
            return SLEEP_ERR_FLOATING_PINS;
        }
    }

    enter_wfi(PWR_CR1_LPMS_STOP2);
    note_wake_source();
    s_stage = SLEEP_STAGE_AWAKE;
    return soft;
}

/* Standby відрізняється двома речами: рівні виводів після засинання задає
 * блок PWR, і вихід із нього — це скидання, а не продовження коду. */
sleep_err_t lowpower_enter_standby(uint32_t seconds)
{
    s_stage = SLEEP_STAGE_AWAKE;
    stage_park_buses();

    sleep_err_t err = stage_rail_off();
    if (err != SLEEP_OK && err != SLEEP_ERR_RAIL_POWERED) {
        return err;
    }
    err = stage_pins_analog();
    if (err != SLEEP_OK) {
        return err;
    }
    (void)stage_debug_silent();

    board_apply_standby_pulls();

    err = stage_arm_wake(seconds);
    if (err != SLEEP_OK) {
        return err;
    }

    PWR_SCR = PWR_SCR_CWUF_ALL | PWR_SCR_CSBF;
    enter_wfi(PWR_CR1_LPMS_STANDBY);

    /* Сюди керування не повертається: пробудження зі Standby йде через скидання.
     * Якщо ми все ж тут — Standby не відбувся, і причина зазвичай одна. */
    return debug_probe_attached() ? SLEEP_ERR_PROBE_ATTACHED : SLEEP_ERR_SEQUENCE;
}

/* Переривання таймера пробудження. Тіло коротке: єдина його робота —
 * зняти прапорці, інакше подія негайно розбудить ядро вдруге. */
void RTC_WKUP_IRQHandler(void)
{
    rtc_unlock();
    RTC_ISR &= ~RTC_ISR_WUTF;
    rtc_lock();
    EXTI_PR1 = EXTI_LINE_RTC_WAKEUP;
}

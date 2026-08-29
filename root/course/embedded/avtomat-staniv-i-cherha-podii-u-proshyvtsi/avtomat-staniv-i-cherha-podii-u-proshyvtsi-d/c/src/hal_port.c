/*
 * Порт HAL для стенда: замість периферії мікроконтролера — модель станції на
 * настільній машині. Він відтворює саме той сценарій, з якого починається
 * стаття: водій вставляє штекер, прикладає картку, автомобіль просить струм,
 * а через секунду після замикання контактора — у розпал трисекундних
 * перехідних процесів — б'є по кнопці «Грибок».
 *
 * Для справжньої станції цей файл замінюють драйверами GPIO, таймера, АЦП і
 * UART. Жоден інший файл проєкту при цьому не міняється.
 */

#include "hal.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "cp_monitor.h"
#include "isr_sources.h"

#define SIM_END_MS 9000u

/* --------------------------------------------------------- стан моделі ---- */

static uint32_t s_now_ms;
static bool     s_relay_closed;
static bool     s_lock_engaged;
static uint8_t  s_pilot_duty = 100u;
static bool     s_pilot_low;
static bool     s_leds[HAL_LED_COUNT];

/* Що «бачить» станція на лінії пілота: клас задає модель автомобіля. */
static cp_class_t s_line = CP_A;

/* Модель контролера переривань: заборона й черга заявок. */
static bool     s_irq_enabled = true;
static bool     s_in_isr;
static uint32_t s_pending_ticks;
static uint32_t s_relay_closed_at;

static const char *led_name(hal_led_t led)
{
    switch (led) {
        case HAL_LED_GREEN: return "зелений";
        case HAL_LED_BLUE:  return "синій";
        case HAL_LED_RED:   return "червоний";
        default:            return "?";
    }
}

/* ------------------------------------------------------------ сценарій ---- */

static void feed_rfid_frame(uint32_t card_id)
{
    static const char hex[] = "0123456789ABCDEF";

    uint8_t xored = 0u;
    for (unsigned i = 0; i < 4u; ++i) {
        xored ^= (uint8_t)(card_id >> (8u * i));
    }

    isr_rfid_rx_byte(0x02u);
    for (int shift = 28; shift >= 0; shift -= 4) {
        isr_rfid_rx_byte((uint8_t)hex[(card_id >> shift) & 0xFu]);
    }
    isr_rfid_rx_byte((uint8_t)hex[(xored >> 4) & 0xFu]);
    isr_rfid_rx_byte((uint8_t)hex[xored & 0xFu]);
    isr_rfid_rx_byte(0x03u);
}

/* Події зовнішнього світу, прив'язані до модельного часу. */
static void run_scenario(uint32_t t)
{
    switch (t) {
        case 500u:
            printf("[%5u мс] водій вставив штекер\n", t);
            s_line = CP_B;
            break;

        case 1200u:
            printf("[%5u мс] прикладено картку 0x04A1B2C3\n", t);
            feed_rfid_frame(0x04A1B2C3u);
            break;

        case 2000u:
            printf("[%5u мс] автомобіль замкнув ключ: запит енергії\n", t);
            s_line = CP_C;
            break;

        case 3000u:
            printf("[%5u мс] *** водій б'є по кнопці аварійної зупинки ***\n", t);
            isr_emergency_button();
            break;

        default:
            break;
    }

    /* Компаратор струму опитує силову лінію щомилісекунди й заявляє
     * переривання лише понад 40 А. */
    if (s_relay_closed) {
        const uint32_t since_close = t - s_relay_closed_at;
        const uint16_t amperes     = (since_close < 200u) ? 80u : 32u;
        if (amperes > 40u) {
            isr_overcurrent(amperes);
        }
    }
}

/* --------------------------------------------- модель контролера NVIC ---- */

static void service_pending(void)
{
    if (s_in_isr || !s_irq_enabled) {
        return;
    }
    s_in_isr = true;
    while (s_pending_ticks > 0u) {
        --s_pending_ticks;
        isr_systick_1ms();
        run_scenario(s_now_ms);
    }
    s_in_isr = false;
}

uint32_t hal_irq_save(void)
{
    const uint32_t was = s_irq_enabled ? 1u : 0u;
    s_irq_enabled      = false;
    return was;
}

void hal_irq_restore(uint32_t saved)
{
    s_irq_enabled = (saved != 0u);
    service_pending();
}

void hal_wait_for_interrupt(void)
{
    /*
     * Модель інструкції WFI: час стоїть, поки не настане наступна апаратна
     * подія. На справжньому кристалі саме тут споживання падає з 25 мА до
     * одиниць мікроампер.
     */
    if (s_now_ms >= SIM_END_MS) {
        printf("[%5u мс] кінець сценарію\n", s_now_ms);
        exit(0);
    }
    ++s_now_ms;
    ++s_pending_ticks;
    /* Заявка стоїть у NVIC; обробник запуститься, коли головний цикл зніме
     * заборону переривань — так само, як на Cortex-M із виставленим PRIMASK. */
}

/* -------------------------------------------------------- реалізація ---- */

void hal_init(void)
{
    s_now_ms       = 0u;
    s_relay_closed = false;
    s_lock_engaged = false;
    s_pilot_duty   = 100u;
    s_pilot_low    = false;
    s_line         = CP_A;
    printf("[    0 мс] станція увімкнена\n");
}

uint32_t hal_millis(void)
{
    return s_now_ms;
}

void hal_relay_set(bool closed)
{
    if (closed == s_relay_closed) {
        return;
    }
    s_relay_closed = closed;
    if (closed) {
        s_relay_closed_at = s_now_ms;
    }
    printf("[%5u мс] силовий контактор %s\n", s_now_ms,
           closed ? "ЗАМКНЕНО" : "розімкнено");
}

bool hal_relay_is_closed(void)
{
    return s_relay_closed;
}

void hal_pilot_set_duty(uint8_t duty_percent)
{
    s_pilot_low  = false;
    s_pilot_duty = (duty_percent > 100u) ? 100u : duty_percent;
}

void hal_pilot_force_low(void)
{
    s_pilot_low = true;
    /* Автомобіль зобов'язаний розімкнути власний контактор і відпустити ключ. */
    s_line = CP_A;
}

int16_t hal_pilot_read_high_mv(void)
{
    if (s_pilot_low) {
        return 0;
    }
    switch (s_line) {
        case CP_B: return 9000;
        case CP_C: return 6000;
        default:   return 12000;
    }
}

int16_t hal_pilot_read_low_mv(void)
{
    /* Діод в автомобілі справний: від'ємний півперіод сягає −12 В. */
    return s_pilot_low ? 0 : -12000;
}

uint32_t hal_pilot_period_us(void)
{
    return (s_pilot_duty >= 100u || s_pilot_low) ? 0u : 1000u;
}

uint16_t hal_leakage_read_ma(void)
{
    return 2u; /* фоновий витік ємності кабелю */
}

void hal_led_set(hal_led_t led, bool on)
{
    if ((unsigned)led >= (unsigned)HAL_LED_COUNT || s_leds[led] == on) {
        return;
    }
    s_leds[led] = on;
    printf("[%5u мс] світлодіод %s %s\n", s_now_ms, led_name(led),
           on ? "увімкнено" : "вимкнено");
}

void hal_lock_actuator(bool locked)
{
    if (locked == s_lock_engaged) {
        return;
    }
    s_lock_engaged = locked;
    printf("[%5u мс] замок роз'єму %s\n", s_now_ms,
           locked ? "закрито" : "відкрито");
}

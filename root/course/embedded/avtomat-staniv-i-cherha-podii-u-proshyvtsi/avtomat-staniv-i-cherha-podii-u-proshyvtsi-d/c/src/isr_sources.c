#include "isr_sources.h"

#include <stdatomic.h>
#include <stdbool.h>

#include "event_queue.h"
#include "hal.h"
#include "soft_timer.h"

/* Кадр зчитувача: STX, вісім шістнадцяткових цифр номера, дві цифри
 * контрольної суми, ETX — саме так віддають картку поширені модулі RDM6300 у
 * 32-бітному режимі. */
#define RFID_STX 0x02u
#define RFID_ETX 0x03u
#define RFID_ID_DIGITS 8u
#define RFID_PAYLOAD_LEN 10u

/* Механічний контакт кнопки деренчить одиниці мілісекунд. */
#define BUTTON_DEBOUNCE_MS 50u

static _Atomic uint32_t s_last_card;

static uint32_t s_tick_counter;
static uint32_t s_emergency_last_ms;
static uint32_t s_reset_last_ms;

static uint8_t  s_rfid_buf[RFID_PAYLOAD_LEN];
static uint8_t  s_rfid_len;
static bool     s_rfid_in_frame;

void isr_sources_init(void)
{
    atomic_store_explicit(&s_last_card, 0u, memory_order_relaxed);
    s_tick_counter      = 0u;
    s_emergency_last_ms = 0u;
    s_reset_last_ms     = 0u;
    s_rfid_len          = 0u;
    s_rfid_in_frame     = false;
}

void isr_systick_1ms(void)
{
    const uint32_t now = hal_millis();

    soft_timer_tick(now);

    if (++s_tick_counter >= 10u) {
        s_tick_counter = 0u;
        /* Сам вимір лінії пілота робить головний цикл: тут лише позначка, що
         * час настав. Читання трьох каналів АЦП у перериванні затримало б
         * приймач UART і зіпсувало б кадр картки. */
        (void)event_queue_push(&g_events, EVT_TICK_10MS, 0u);
    }
}

/* Придушення деренчання просто в обробнику: подія народжується лише з першого
 * фронту, решта імпульсів у вікні відкидається без звернення до черги. */
static bool debounce_passed(uint32_t *last_ms)
{
    const uint32_t now = hal_millis();
    if (*last_ms != 0u && (uint32_t)(now - *last_ms) < BUTTON_DEBOUNCE_MS) {
        return false;
    }
    *last_ms = now;
    return true;
}

void isr_emergency_button(void)
{
    if (debounce_passed(&s_emergency_last_ms)) {
        (void)event_queue_push(&g_events, EVT_EMERGENCY_STOP, 0u);
    }
}

void isr_reset_button(void)
{
    if (debounce_passed(&s_reset_last_ms)) {
        (void)event_queue_push(&g_events, EVT_RESET_BUTTON, 0u);
    }
}

void isr_overcurrent(uint16_t amperes)
{
    (void)event_queue_push(&g_events, EVT_OVERCURRENT, amperes);
}

void isr_leakage(uint16_t milliamps)
{
    (void)event_queue_push(&g_events, EVT_LEAKAGE_TRIP, milliamps);
}

static uint8_t hex_digit(uint8_t c)
{
    if (c >= '0' && c <= '9') return (uint8_t)(c - '0');
    if (c >= 'A' && c <= 'F') return (uint8_t)(c - 'A' + 10);
    if (c >= 'a' && c <= 'f') return (uint8_t)(c - 'a' + 10);
    return 0xFFu; /* не шістнадцяткова цифра */
}

void isr_rfid_rx_byte(uint8_t byte)
{
    if (byte == RFID_STX) {
        s_rfid_in_frame = true;
        s_rfid_len      = 0u;
        return;
    }

    if (!s_rfid_in_frame) {
        return; /* сміття між кадрами */
    }

    if (byte == RFID_ETX) {
        s_rfid_in_frame = false;
        if (s_rfid_len != RFID_PAYLOAD_LEN) {
            return; /* обірваний кадр */
        }

        uint32_t id       = 0u;
        uint8_t  checksum = 0u;
        for (unsigned i = 0; i < RFID_ID_DIGITS; ++i) {
            const uint8_t d = hex_digit(s_rfid_buf[i]);
            if (d == 0xFFu) {
                return;
            }
            id = (id << 4) | d;
        }
        for (unsigned i = RFID_ID_DIGITS; i < RFID_PAYLOAD_LEN; ++i) {
            const uint8_t d = hex_digit(s_rfid_buf[i]);
            if (d == 0xFFu) {
                return;
            }
            checksum = (uint8_t)((checksum << 4) | d);
        }

        /* Контрольна сума: XOR усіх чотирьох байтів номера. */
        uint8_t xored = 0u;
        for (unsigned i = 0; i < 4u; ++i) {
            xored ^= (uint8_t)(id >> (8u * i));
        }
        if (xored != checksum) {
            return; /* завада на лінії: кадр відкинуто, події не буде */
        }

        atomic_store_explicit(&s_last_card, id, memory_order_release);
        (void)event_queue_push(&g_events, EVT_RFID_TAG, (uint16_t)(id & 0xFFFFu));
        return;
    }

    if (s_rfid_len < RFID_PAYLOAD_LEN) {
        s_rfid_buf[s_rfid_len++] = byte;
    } else {
        s_rfid_in_frame = false; /* кадр довший за очікуваний — викидаємо */
    }
}

uint32_t isr_rfid_last_card(void)
{
    return atomic_load_explicit(&s_last_card, memory_order_acquire);
}

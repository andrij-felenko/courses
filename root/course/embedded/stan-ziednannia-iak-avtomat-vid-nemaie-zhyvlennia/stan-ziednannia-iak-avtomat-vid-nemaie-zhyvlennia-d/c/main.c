#include "at_link.h"
#include "blackbox.h"
#include "conn_fsm.h"
#include "modem_hal.h"

#include <stdbool.h>
#include <stdint.h>

#define TICK_MS    20u
#define SESSION_MS 86400000u /* сеанс раз на добу */

static conn_fsm_t g_conn;

/* Міст із вектора переривання UART плати. */
void app_uart_rx_isr(uint8_t byte)
{
    at_link_rx_isr(byte);
}

/* Давач рівня — те, заради чого вузол узагалі виходить в ефір. */
uint16_t sensor_read_level_mm(void);

static size_t build_telemetry(uint8_t *buf, size_t cap)
{
    if (cap < 10u) {
        return 0;
    }
    uint32_t t = hal_now_ms();
    uint16_t level = sensor_read_level_mm();
    uint16_t vbat = hal_vbat_mv();
    uint16_t lost = (uint16_t)at_link_overflows();

    buf[0] = (uint8_t)(t & 0xFFu);
    buf[1] = (uint8_t)((t >> 8) & 0xFFu);
    buf[2] = (uint8_t)((t >> 16) & 0xFFu);
    buf[3] = (uint8_t)((t >> 24) & 0xFFu);
    buf[4] = (uint8_t)(level & 0xFFu);
    buf[5] = (uint8_t)(level >> 8);
    buf[6] = (uint8_t)(vbat & 0xFFu);
    buf[7] = (uint8_t)(vbat >> 8);
    buf[8] = (uint8_t)(lost & 0xFFu);
    buf[9] = (uint8_t)(lost >> 8);
    return 10u;
}

int main(void)
{
    board_init();
    at_link_init();
    blackbox_init();
    conn_fsm_init(&g_conn);

    uint32_t next_tick = hal_now_ms();
    uint32_t next_session = hal_now_ms();
    bool session_open = false;

    for (;;) {
        /* Автомат неблокуючий, тож сторожа гладимо щотакту, а не «коли встигнемо». */
        hal_watchdog_kick();

        uint32_t now = hal_now_ms();

        if ((int32_t)(now - next_session) >= 0) {
            uint8_t frame[16];
            size_t n = build_telemetry(frame, sizeof(frame));

            next_session += SESSION_MS;
            conn_fsm_connect(&g_conn);
            (void)conn_fsm_submit(&g_conn, frame, n);
            session_open = true;
        }

        if ((int32_t)(now - next_tick) >= 0) {
            next_tick += TICK_MS;
            conn_fsm_tick(&g_conn);
        }

        /* Дані підтверджено брокером — згортаємо сеанс і йдемо спати.
           Якщо автомат зупинився фатально, сюди він просто не доходить,
           і наступний добовий сеанс почне все з нуля. */
        if (session_open && conn_fsm_idle(&g_conn)) {
            conn_fsm_disconnect(&g_conn);
            session_open = false;
        }
    }
}

/* ports/host_mock/host_port.c — плата, якої немає.
 * Час тут віртуальний: hal_cpu_sleep() не спить, а переводить годинник
 * уперед до наступного тіку й кладе подію в чергу. Прошивка від цього
 * не змінюється жодним рядком, зате доба роботи проходить за мить, і
 * складання на кожен коміт стає реальним. */
#include "include/board.h"
#include "include/sys_config.h"
#include "hal/hal_critical.h"
#include "hal/hal_time.h"
#include "ports/host_mock/host_port.h"
#include "services/event_queue.h"

#include <stdio.h>

#define HOST_LED_PIN   0u

static uint32_t       g_virtual_ms;
static uint32_t       g_next_tick_ms = SYS_TICK_PERIOD_MS;
static event_queue_t *g_queue;
static board_t        g_board;

/* --- hal/hal_time.h --- */

uint32_t hal_time_now_ms(void)
{
    return g_virtual_ms;
}

void hal_time_delay_ms(uint32_t ms)
{
    g_virtual_ms += ms;
}

void hal_cpu_sleep(void)
{
    /* Стрибаємо просто до моменту наступного тіку — рівно так, як ядро
     * прокидається з WFI від переривання таймера. */
    if ((int32_t)(g_next_tick_ms - g_virtual_ms) > 0) {
        g_virtual_ms = g_next_tick_ms;
    }
    g_next_tick_ms = g_virtual_ms + SYS_TICK_PERIOD_MS;

    if (g_queue != 0) {
        const sys_event_t evt = sys_event_make(EVT_ID_TICK_100MS, g_virtual_ms);
        (void)event_queue_post(g_queue, &evt);
    }
}

/* --- hal/hal_critical.h --- */

uint32_t hal_critical_enter(void)
{
    /* На хості справжніх переривань немає, тож секція порожня. Функції
     * лишаються на місці навмисно: код черги подій має бути той самий,
     * інакше тест перевіряв би не ту прошивку, що поїде на плату. */
    return 0u;
}

void hal_critical_exit(uint32_t saved_state)
{
    (void)saved_state;
}

/* --- include/board.h --- */

void board_bind_event_queue(struct event_queue *queue)
{
    g_queue = queue;
}

struct event_queue *board_event_queue(void)
{
    return g_queue;
}

void mock_button_click(void)
{
    if (g_queue == 0) {
        return;
    }
    sys_event_t evt = sys_event_make(EVT_ID_BUTTON_CLICK, g_virtual_ms);
    evt.data.button_pin = 0u;
    (void)event_queue_post(g_queue, &evt);
}

static void host_report_record(void *ctx, const telemetry_record_t *rec)
{
    (void)ctx;
    if (rec == 0) {
        return;
    }
    printf("[%8u ms] T=%.2f C (%.2f…%.2f) H=%.1f%% P=%.2f hPa "
           "VIB rms=%.3f g peak=%.3f g N=%u ERR=%u\n",
           (unsigned)rec->window_end_ms,
           (double)rec->temp_avg_c,
           (double)rec->temp_min_c,
           (double)rec->temp_max_c,
           (double)rec->humidity_avg_rh,
           (double)rec->pressure_avg_hpa,
           (double)rec->vibration_rms_g,
           (double)rec->vibration_peak_g,
           (unsigned)rec->sample_count,
           (unsigned)rec->fault_count);
}

const board_t *board_init(void)
{
    g_virtual_ms   = 0u;
    g_next_tick_ms = SYS_TICK_PERIOD_MS;

    const hal_i2c_bus_t *bus = mock_i2c_bus();

    g_board.env_bus   = bus;
    g_board.accel_bus = bus;

    g_board.led_status.ops        = mock_gpio_ops();
    g_board.led_status.ctx        = mock_gpio_port();
    g_board.led_status.pin        = HOST_LED_PIN;
    g_board.led_status.active_low = false;

    g_board.report_record = host_report_record;
    g_board.report_ctx    = 0;

    return &g_board;
}

#include "cp_monitor.h"
#include "event_queue.h"
#include "evse.h"
#include "hal.h"
#include "isr_sources.h"
#include "soft_timer.h"

/*
 * Головний цикл усієї прошивки. Він не знає ні про зарядну станцію, ні про
 * лінію пілота: його робота — витягти подію, віддати її автомату й заснути,
 * коли віддавати нічого.
 */
int main(void)
{
    hal_init();
    event_queue_init(&g_events);
    soft_timer_init();
    cp_monitor_init();
    isr_sources_init();
    evse_init(&g_evse);

    uint16_t last_dropped = 0u;

    for (;;) {
        event_t e;

        while (event_queue_pop(&g_events, &e)) {
            /* Повільні опитування живуть тут, у потоці головного циклу, а не
             * в обробнику таймера. */
            if (e.id == EVT_TICK_10MS) {
                cp_monitor_sample();
            }

            /* Run-To-Completion: подія обробляється до кінця, і лише потім
             * береться наступна. Усередині evse_dispatch() ніхто не чекає й
             * не спить, тому черга не встигає накопичитися. */
            evse_dispatch(&g_evse, &e);
        }

        /*
         * Утрата події означає, що ми проґавили щось невідоме — можливо, саме
         * аварію. Єдина безпечна відповідь — знеструмити лінію.
         */
        const uint16_t dropped = event_queue_dropped(&g_events);
        if (dropped != last_dropped) {
            last_dropped = dropped;
            (void)event_queue_push(&g_events, EVT_EMERGENCY_STOP, 0u);
            continue;
        }

        /*
         * Перевірка порожньої черги й засинання мусять бути неподільні. Якби
         * переривання вклинилося між ними, воно поклало б подію в чергу вже
         * після перевірки — і ядро заснуло б до наступного, ні з чим не
         * пов'язаного переривання. WFI прокидається й із забороненими
         * перериваннями, тож заборона тут не заважає, а рятує.
         */
        const uint32_t saved = hal_irq_save();
        if (event_queue_is_empty(&g_events)) {
            hal_wait_for_interrupt();
        }
        hal_irq_restore(saved);
    }
}

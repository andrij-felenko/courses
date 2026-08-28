#include "soc/gpio_struct.h"   // GPIO.out_w1ts / GPIO.enable_w1ts — регістри GPIO
#include "soc/gpio_periph.h"   // GPIO_PIN_MUX_REG[] — регістр IO_MUX кожної ніжки
#include "soc/io_mux_reg.h"    // PIN_FUNC_SELECT, PIN_FUNC_GPIO
#include "esp_timer.h"
#include "esp_log.h"

#define BOOT_MARK_GPIO  2      // вільна ніжка під щуп аналізатора (0..31)

void app_main(void)
{
    // НАЙПЕРША дія — маркер абсолютного нуля прошивки, трьома прямими
    // записами в регістри, без драйвера GPIO. Спершу дозволити ніжці
    // «говорити», аж потім різко підняти.

    // 1. Завести пад на функцію GPIO в IO_MUX: після скидання пад може
    //    сидіти на іншій функції й регістра out просто не слухати.
    PIN_FUNC_SELECT(GPIO_PIN_MUX_REG[BOOT_MARK_GPIO], PIN_FUNC_GPIO);

    // 2. Увімкнути вихідний драйвер ніжки: після скидання enable = 0,
    //    тобто ніжка «слухає», а не «говорить», і запис у out на неї не діє.
    GPIO.enable_w1ts = (1u << BOOT_MARK_GPIO);

    // 3. Різко підняти: саме цей запис дає фронт, який ловить аналізатор.
    //    w1ts = write-1-to-set: одиниця у біті ставить пін, нулі — без впливу.
    GPIO.out_w1ts = (1u << BOOT_MARK_GPIO);

    // одразу за маркером — внутрішній відлік третьої ланки
    int64_t t_idf_us = esp_timer_get_time();   // мкс від старту ESP-IDF

    // ... далі звичайний старт застосунку; ніжку згодом можна опустити ...
    // GPIO.out_w1tc = (1u << BOOT_MARK_GPIO);  // write-1-to-clear, коли треба
}

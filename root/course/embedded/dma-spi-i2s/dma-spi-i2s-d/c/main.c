#include "driver/i2s_std.h"
#include <string.h>

#define N            256          /* відліків у буфері */
#define RING         8            /* дескрипторів у кільці */

static i2s_chan_handle_t tx, rx;

/* Заповнити ЦІЛЕ кільце тишею до старту передавача (prefill).
   Без цього перший блок у підсилювач піде сміттям із порожньої RAM. */
static void i2s_tx_prefill(void)
{
    int16_t silence[N * 2] = { 0 };   /* стерео: L,R,L,R... нулі */
    size_t written;
    for (int i = 0; i < RING; i++) {
        /* кладемо блок за блоком, поки кільце не заповнене;
           timeout 0 — щойно кільце повне, виклик поверне ESP_ERR_TIMEOUT */
        if (i2s_channel_write(tx, silence, sizeof(silence),
                              &written, 0) != ESP_OK)
            break;
    }
}

void i2s_duplex_start(void)
{
    i2s_tx_prefill();                 /* СПЕРШУ наповнити вихід */
    i2s_channel_enable(tx);           /* тепер безпечно стартувати передавач */
    i2s_channel_enable(rx);           /* і приймач */

    int32_t buf[N];
    size_t  got;
    for (;;) {
        /* Перший виклик чекатиме цілий T_fill = N/f_s, поки DMA
           наповнить перший буфер приймання — це нормальна стартова затримка. */
        i2s_channel_read(rx, buf, sizeof(buf), &got, portMAX_DELAY);

        int n = got / sizeof(int32_t);   /* ФАКТИЧНА довжина: на краях блок неповний */
        for (int i = 0; i < n; i++) {
            int32_t s = buf[i] >> 8;      /* 24 значущі біти у старших розрядах */
            /* ...обробити відлік s, встигнути за T_proc < T_fill... */
        }
    }
}

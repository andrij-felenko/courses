/* збірка:
     git clone https://github.com/mavlink/c_library_v2
     cc -std=c11 -O2 -Wall -I c_library_v2 rxdemo.c -o rxdemo            */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <common/mavlink.h>

#define RX_NO_CHANNEL 0xFFu

static uint32_t g_channel_mask;

static uint8_t channel_take(void)
{
    for (uint8_t chan = 0; chan < MAVLINK_COMM_NUM_BUFFERS; ++chan) {
        if (g_channel_mask & (1u << chan)) {
            continue;
        }

        mavlink_reset_channel_status(chan);   /* скидає ЛИШЕ фазу автомата */

        mavlink_status_t *st = mavlink_get_channel_status(chan);
        st->flags                   = 0;      /* версія входу й виходу     */
        st->signing                 = NULL;   /* ключ попереднього з'єднання */
        st->signing_streams         = NULL;
        st->current_tx_seq          = 0;
        st->packet_rx_success_count = 0;

        g_channel_mask |= (1u << chan);
        return chan;
    }
    return RX_NO_CHANNEL;   /* слотів більше немає */
}

static void channel_give(uint8_t chan)
{
    if (chan >= MAVLINK_COMM_NUM_BUFFERS) {
        return;
    }
    mavlink_reset_channel_status(chan);
    g_channel_mask &= ~(1u << chan);
}

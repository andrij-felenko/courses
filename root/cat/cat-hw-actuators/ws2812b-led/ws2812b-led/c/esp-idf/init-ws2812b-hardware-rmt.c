// Апаратна генерація сигналу WS2812B через RMT та DMA в ESP-IDF (C)
#include "driver/rmt_tx.h"
#include "led_strip_types.h"

void init_ws2812b_hardware_rmt(gpio_num_t gpio_pin) {
    rmt_tx_channel_config_t tx_chan_config = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .gpio_num = gpio_pin,
        .mem_block_symbols = 64,
        .resolution_hz = 10000000, // 10 МГц роздільна здатність (100 нс на тик)
        .trans_queue_depth = 4,
    };
    rmt_channel_handle_t tx_channel = NULL;
    rmt_new_tx_channel(&tx_chan_config, &tx_channel);
    rmt_enable(tx_channel);
}

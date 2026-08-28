#include "driver/rmt_tx.h"

static rmt_channel_handle_t chan;              // канал RMT — «магнітофон» таймінгів

void ir_begin(int gpio) {                      // вивід будь-який вільний
    rmt_tx_channel_config_t cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .gpio_num = gpio,
        .resolution_hz = 1000000,              // 1 тік = 1 мкс
        .mem_block_symbols = 64,
        .trans_queue_depth = 4,
    };
    ESP_ERROR_CHECK(rmt_new_tx_channel(&cfg, &chan));

    rmt_carrier_config_t carrier = {           // несучу домішує сама апаратура
        .frequency_hz = 38000,
        .duty_cycle = 0.33,
    };
    ESP_ERROR_CHECK(rmt_apply_carrier(chan, &carrier));
    ESP_ERROR_CHECK(rmt_enable(chan));
}

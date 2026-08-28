#include "driver/i2s_std.h"

static i2s_chan_handle_t tx_chan;

void i2s_out_init(void) {
    /* один канал передачі на контролері I2S0, роль — майстер */
    i2s_chan_config_t chan_cfg =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    i2s_new_channel(&chan_cfg, &tx_chan, NULL);   /* лише TX */

    i2s_std_config_t std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(44100),                 /* 44.1 кГц */
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
                        I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .bclk = GPIO_NUM_26,   /* BCLK  → BCLK підсилювача */
            .ws   = GPIO_NUM_25,   /* WS    → LRC  підсилювача */
            .dout = GPIO_NUM_22,   /* SD    → DIN  підсилювача */
            .din  = I2S_GPIO_UNUSED,
        },
    };
    i2s_channel_init_std_mode(tx_chan, &std_cfg);
    i2s_channel_enable(tx_chan);
}

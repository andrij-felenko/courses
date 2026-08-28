#include "driver/i2s_pdm.h"

static i2s_chan_handle_t pdm_tx;

void pdm_out_init(void) {
    i2s_chan_config_t chan_cfg =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    i2s_new_channel(&chan_cfg, &pdm_tx, NULL);

    i2s_pdm_tx_config_t pdm_cfg = {
        .clk_cfg  = I2S_PDM_TX_CLK_DEFAULT_CONFIG(44100),
        .slot_cfg = I2S_PDM_TX_SLOT_DEFAULT_CONFIG(
                        I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .clk  = GPIO_NUM_26,   /* такт PDM */
            .dout = GPIO_NUM_25,   /* однобітний потік */
        },
    };
    i2s_channel_init_pdm_tx_mode(pdm_tx, &pdm_cfg);  /* PCM → PDM усередині */
    i2s_channel_enable(pdm_tx);
    /* далі — той самий i2s_channel_write() з PCM-відліками */
}

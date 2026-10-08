#include "driver/i2s_std.h"
#include "driver/gpio.h"

static i2s_chan_handle_t rx_handle;

void init_i2s_mems_microphone(void) {
    // Конфігурація каналу I2S у режимі Master RX
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    i2s_new_channel(&chan_cfg, NULL, &rx_handle);

    // Конфігурація тактування, слотів та GPIO для стандарту I2S
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(44100),
        .slot_cfg = I2S_STD_MSB_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = GPIO_NUM_4,
            .ws = GPIO_NUM_5,
            .dout = I2S_GPIO_UNUSED,
            .din = GPIO_NUM_18,
            .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
        },
    };

    i2s_channel_init_std_mode(rx_handle, &std_cfg);
    i2s_channel_enable(rx_handle);
}

void read_audio_samples(int32_t *out_buffer, size_t samples_count) {
    size_t bytes_read = 0;
    // Зчитування звукового потоку через DMA без блокування CPU
    i2s_channel_read(rx_handle, out_buffer, samples_count * sizeof(int32_t), &bytes_read, portMAX_DELAY);

    // Арифметичне вирівнювання: зсув 24-бітного значення у 32-бітному слоті
    for (size_t i = 0; i < samples_count; i++) {
        out_buffer[i] = out_buffer[i] >> 8;
    }
}

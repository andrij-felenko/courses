#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"

#define I2S_BCLK_PIN    GPIO_NUM_14
#define I2S_WS_PIN      GPIO_NUM_25
#define I2S_DATA_PIN    GPIO_NUM_33

#define SAMPLE_RATE     44100
#define DMA_BUF_LEN     512

static i2s_chan_handle_t rx_handle = NULL;

void init_i2s_mems(void) {
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num = 6;
    chan_cfg.dma_frame_num = DMA_BUF_LEN;
    
    i2s_new_channel(&chan_cfg, NULL, &rx_handle);

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_BCLK_PIN,
            .ws = I2S_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din = I2S_DATA_PIN,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;

    i2s_channel_init_std_mode(rx_handle, &std_cfg);
    i2s_channel_enable(rx_handle);
}

void process_audio_stream(void) {
    int32_t raw_samples[DMA_BUF_LEN];
    size_t bytes_read = 0;
    static int32_t prev_x = 0;
    static float prev_y = 0.0f;
    const float alpha = 0.995f;

    while (1) {
        if (i2s_channel_read(rx_handle, raw_samples, sizeof(raw_samples), &bytes_read, portMAX_DELAY) == ESP_OK) {
            size_t sample_count = bytes_read / sizeof(int32_t);
            for (size_t i = 0; i < sample_count; i++) {
                // Бітове вирівнювання: 24-бітний семпл у старших бітах 32-бітного слова
                int32_t aligned_sample = raw_samples[i] >> 8;
                
                // Видалення DC-зсуву (ФВЧ 1-го порядку)
                float current_x = (float)aligned_sample;
                float filtered_y = current_x - (float)prev_x + alpha * prev_y;
                prev_x = (int32_t)current_x;
                prev_y = filtered_y;
                
                int32_t pcm_out = (int32_t)filtered_y;
                (void)pcm_out; // Очищений відліковий PCM-синал готовий для обробки
            }
        }
    }
}

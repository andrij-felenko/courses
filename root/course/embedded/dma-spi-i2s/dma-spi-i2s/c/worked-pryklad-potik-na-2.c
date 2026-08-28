#include "driver/i2s.h"

void i2s_mic_init(void) {
    i2s_config_t cfg = {
        .mode            = I2S_MODE_MASTER | I2S_MODE_RX,
        .sample_rate     = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format  = I2S_CHANNEL_FMT_ONLY_LEFT,
        .dma_buf_count   = 8,            /* вісім буферів у кільці */
        .dma_buf_len     = 256,          /* по 256 відліків кожен */
    };
    i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
    /* i2s_set_pin(...) — вивести BCLK / WS / DIN на GPIO */
}

void i2s_mic_task(void *arg) {
    int32_t buf[256];
    size_t  got;
    for (;;) {
        /* блокуємось, доки DMA не наповнить черговий буфер кільця */
        i2s_read(I2S_NUM_0, buf, sizeof(buf), &got, portMAX_DELAY);
        int n = got / sizeof(int32_t);
        for (int i = 0; i < n; i++) {
            int32_t s = buf[i] >> 8;     /* 24 значущі біти — у старших розрядах */
            /* ...обробити відлік s... */
        }
    }
}

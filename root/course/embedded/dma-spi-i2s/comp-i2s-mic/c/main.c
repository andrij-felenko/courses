#include "driver/i2s.h"
#include "esp_log.h"

#define I2S_NUM        I2S_NUM_0
#define SAMPLE_RATE    16000
#define GPIO_BCLK      26
#define GPIO_WS        25
#define GPIO_DIN       34   // тільки вхід

void i2s_mic_init(void) {
    /* Конфігурація I2S-периферії з DMA-кільцем:
       8 буферів по 256 відліків — кільце подвійних буферів у дії. */
    i2s_config_t cfg = {
        .mode                 = I2S_MODE_MASTER | I2S_MODE_RX,
        .sample_rate          = SAMPLE_RATE,
        .bits_per_sample      = I2S_BITS_PER_SAMPLE_32BIT,   /* слот 32 біти */
        .channel_format       = I2S_CHANNEL_FMT_ONLY_LEFT,   /* L/R на GND */
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,   /* Philips */
        .dma_buf_count        = 8,    /* вісім DMA-буферів у кільці */
        .dma_buf_len          = 256,  /* 256 відліків кожен */
        .use_apll             = false,
        .intr_alloc_flags     = 0,
    };

    i2s_pin_config_t pins = {
        .bck_io_num   = GPIO_BCLK,
        .ws_io_num    = GPIO_WS,
        .data_in_num  = GPIO_DIN,
        .data_out_num = I2S_PIN_NO_CHANGE,  /* TX не потрібен */
    };

    i2s_driver_install(I2S_NUM, &cfg, 0, NULL);
    i2s_set_pin(I2S_NUM, &pins);
}

void i2s_mic_task(void *arg) {
    int32_t buf[256];
    size_t  bytes_read;

    for (;;) {
        /* Блокуємось, доки DMA не наповнить черговий буфер */
        i2s_read(I2S_NUM, buf, sizeof(buf), &bytes_read, portMAX_DELAY);

        /* INMP441: 24 значущих біти у старших розрядах 32-бітного слова */
        int64_t sum_sq = 0;
        int n = bytes_read / sizeof(int32_t);
        for (int i = 0; i < n; i++) {
            int32_t s = buf[i] >> 8;   /* зсунути: старші 24 → нижні розряди */
            sum_sq += (int64_t)s * s;
        }
        /* Корінь із середнього квадрату — ознака амплітуди */
        int32_t rms = (int32_t)sqrt((double)sum_sq / n);
        ESP_LOGI("MIC", "RMS = %ld", (long)rms);
    }
}

#include <driver/i2s.h>

#define I2S_BCLK_PIN  GPIO_NUM_4
#define I2S_WS_PIN    GPIO_NUM_5
#define I2S_DATA_PIN  GPIO_NUM_18

void setupI2SMicrophone() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 512,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCLK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DATA_PIN
    };

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
}

void readAndAlignAudio(int32_t *buffer, size_t count) {
    size_t bytes_read = 0;
    i2s_read(I2S_NUM_0, buffer, count * sizeof(int32_t), &bytes_read, portMAX_DELAY);
    
    for (size_t i = 0; i < count; i++) {
        buffer[i] = buffer[i] >> 8; // Зсув старших бітів для нормалізації PCM
    }
}

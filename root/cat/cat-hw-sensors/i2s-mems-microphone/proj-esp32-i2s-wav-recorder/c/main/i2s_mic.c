/**
 * @file i2s_mic.c
 * @brief Реалізація процедур драйвера I2S-мікрофона INMP441 для ESP32.
 */

#include "i2s_mic.h"
#include <string.h>
#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "I2S_MIC";

static i2s_port_t g_i2s_port = I2S_NUM_0;

esp_err_t i2s_mic_init(const i2s_mic_config_t *config, i2s_mic_dev_t *dev)
{
    if (config == NULL || dev == NULL) {
        ESP_LOGE(TAG, "Помилка: нульовий вказівник у i2s_mic_init");
        return ESP_ERR_INVALID_ARG;
    }

    memset(dev, 0, sizeof(i2s_mic_dev_t));
    g_i2s_port = config->i2s_port;

    /* Налаштування параметрів шини I2S для режиму Master RX */
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = config->sample_rate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = (int)config->dma_desc_num,
        .dma_buf_len = (int)config->dma_frame_num,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    /* Налаштування фізичних пинів GPIO matrix */
    i2s_pin_config_t pin_config = {
        .bck_io_num = config->sck_pin,
        .ws_io_num = config->ws_pin,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = config->sd_pin
    };

    esp_err_t err = i2s_driver_install(config->i2s_port, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося встановити драйвер I2S: %s", esp_err_to_name(err));
        return err;
    }

    err = i2s_set_pin(config->i2s_port, &pin_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося налаштувати пини I2S: %s", esp_err_to_name(err));
        i2s_driver_uninstall(config->i2s_port);
        return err;
    }

    /* Обчислення розміру пінг-понг буфера */
    dev->buffer_capacity_samples = config->dma_frame_num;
    dev->buffer_size_bytes = dev->buffer_capacity_samples * sizeof(int32_t);

    /* Виділення пам'яті у SRAM під подвійний пінг-понг буфер */
    for (int i = 0; i < I2S_MIC_PINGPONG_BUFFERS; i++) {
        dev->raw_buffers[i] = (int32_t *)heap_caps_malloc(dev->buffer_size_bytes, MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
        if (dev->raw_buffers[i] == NULL) {
            ESP_LOGE(TAG, "Нестача пам'яті під DMA буфер %d", i);
            i2s_mic_deinit(dev);
            return ESP_ERR_NO_MEM;
        }
        memset(dev->raw_buffers[i], 0, dev->buffer_size_bytes);
    }

    /* Створення засобів синхронізації FreeRTOS */
    dev->ready_sem = xSemaphoreCreateBinary();
    dev->lock = xSemaphoreCreateMutex();
    if (dev->ready_sem == NULL || dev->lock == NULL) {
        ESP_LOGE(TAG, "Не вдалося створити семафори FreeRTOS");
        i2s_mic_deinit(dev);
        return ESP_ERR_NO_MEM;
    }

    dev->write_index = 0;
    dev->read_index = 1;
    dev->is_running = false;

    ESP_LOGI(TAG, "Драйвер I2S INMP441 успішно ініціалізовано (SampleRate=%lu Гц)", (unsigned long)config->sample_rate);
    return ESP_OK;
}

esp_err_t i2s_mic_start(i2s_mic_dev_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    xSemaphoreTake(dev->lock, portMAX_DELAY);
    i2s_zero_dma_buffer(g_i2s_port);
    i2s_start(g_i2s_port);
    dev->is_running = true;
    xSemaphoreGive(dev->lock);

    ESP_LOGI(TAG, "Захоплення аудіо з I2S мікрофона запущено");
    return ESP_OK;
}

esp_err_t i2s_mic_get_buffer(i2s_mic_dev_t *dev, int32_t **out_buffer, size_t *out_samples, TickType_t wait_ticks)
{
    if (dev == NULL || out_buffer == NULL || out_samples == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!dev->is_running) {
        return ESP_ERR_INVALID_STATE;
    }

    /* Прочитати один повний кадр аудіоданих через I2S DMA у поточний буфер запису */
    size_t bytes_read = 0;
    int32_t *target_buf = dev->raw_buffers[dev->write_index];

    esp_err_t err = i2s_read(g_i2s_port, (void *)target_buf, dev->buffer_size_bytes, &bytes_read, wait_ticks);
    if (err != ESP_OK || bytes_read == 0) {
        return (err == ESP_OK) ? ESP_ERR_TIMEOUT : err;
    }

    xSemaphoreTake(dev->lock, portMAX_DELAY);
    /* Перемикання пінг-понг буферів: записаний стає доступним для читання */
    dev->read_index = dev->write_index;
    dev->write_index = (dev->write_index + 1) % I2S_MIC_PINGPONG_BUFFERS;

    *out_buffer = dev->raw_buffers[dev->read_index];
    *out_samples = bytes_read / sizeof(int32_t);
    xSemaphoreGive(dev->lock);

    return ESP_OK;
}

esp_err_t i2s_mic_release_buffer(i2s_mic_dev_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    /* Буфер повертається в пул після обробки */
    return ESP_OK;
}

esp_err_t i2s_mic_stop(i2s_mic_dev_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    xSemaphoreTake(dev->lock, portMAX_DELAY);
    dev->is_running = false;
    i2s_stop(g_i2s_port);
    xSemaphoreGive(dev->lock);

    ESP_LOGI(TAG, "Захоплення аудіо зупинено");
    return ESP_OK;
}

esp_err_t i2s_mic_deinit(i2s_mic_dev_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    i2s_mic_stop(dev);
    i2s_driver_uninstall(g_i2s_port);

    for (int i = 0; i < I2S_MIC_PINGPONG_BUFFERS; i++) {
        if (dev->raw_buffers[i] != NULL) {
            heap_caps_free(dev->raw_buffers[i]);
            dev->raw_buffers[i] = NULL;
        }
    }

    if (dev->ready_sem != NULL) {
        vSemaphoreDelete(dev->ready_sem);
        dev->ready_sem = NULL;
    }

    if (dev->lock != NULL) {
        vSemaphoreDelete(dev->lock);
        dev->lock = NULL;
    }

    ESP_LOGI(TAG, "Ресурси I2S-драйвера деініціалізовано");
    return ESP_OK;
}

size_t i2s_mic_convert_32to16(const int32_t *src, int16_t *dst, size_t num_samples)
{
    if (src == NULL || dst == NULL) {
        return 0;
    }

    for (size_t i = 0; i < num_samples; i++) {
        /*
         * INMP441 видає 24-бітні знакові PCM-дані, вирівняні по старшому біту (MSB)
         * у 32-бітному слоті I2S.
         * Зсув на 14 біт вправо конвертує 24-бітне значення у 16-бітний знаковий формат.
         */
        int32_t sample = src[i] >> 14;

        /* Захист від насичення/кліпінгу у разі виходу за межі int16_t */
        if (sample > 32767) {
            sample = 32767;
        } else if (sample < -32768) {
            sample = -32768;
        }

        dst[i] = (int16_t)sample;
    }

    return num_samples;
}

/**
 * @file main.c
 * @brief Головний модуль оцифрування аудіо з I2S MEMS-мікрофона INMP441 та запису у WAV-файл на SD-картку.
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_log.h"

#include "sd_card.h"
#include "i2s_mic.h"
#include "wav_writer.h"

static const char *TAG = "MAIN_APP";

/** Тривалість запису аудіо у секундах */
#define RECORD_DURATION_SEC  5

/** Назва файлу запису аудіо */
#define RECORD_FILE_PATH     SD_CARD_MOUNT_POINT "/record_inmp441.wav"

void app_main(void)
{
    ESP_LOGI(TAG, "=== Запуск програми захоплення аудіо з INMP441 у WAV ===");

    /* 1. Ініціалізація энергонезалежної пам'яті NVS */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* 2. Ініціалізація та монтування SD-картки */
    sd_card_config_t sd_cfg = {
        .mount_point = SD_CARD_MOUNT_POINT,
        .pin_miso = SD_CARD_PIN_MISO,
        .pin_mosi = SD_CARD_PIN_MOSI,
        .pin_clk = SD_CARD_PIN_CLK,
        .pin_cs = SD_CARD_PIN_CS,
        .max_files = 3,
        .format_if_mount_failed = 0
    };

    if (sd_card_init(&sd_cfg) != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: не вдалося змонтувати SD-картку. Запис скасовано.");
        return;
    }

    uint64_t free_bytes = 0, total_bytes = 0;
    if (sd_card_get_free_space(&free_bytes, &total_bytes) == ESP_OK) {
        ESP_LOGI(TAG, "SD-картка: вільний обсяг %llu МБ з %llu МБ",
                 free_bytes / (1024 * 1024), total_bytes / (1024 * 1024));
    }

    /* 3. Налаштування драйвера I2S-мікрофона INMP441 */
    i2s_mic_config_t mic_cfg = {
        .i2s_port = I2S_NUM_0,
        .sck_pin = I2S_MIC_DEFAULT_SCK_PIN,
        .ws_pin = I2S_MIC_DEFAULT_WS_PIN,
        .sd_pin = I2S_MIC_DEFAULT_SD_PIN,
        .sample_rate = I2S_MIC_DEFAULT_SAMPLE_RATE,
        .dma_frame_num = I2S_MIC_DEFAULT_DMA_FRAME_NUM,
        .dma_desc_num = I2S_MIC_DEFAULT_DMA_DESC_NUM
    };

    i2s_mic_dev_t mic_dev;
    if (i2s_mic_init(&mic_cfg, &mic_dev) != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати драйвер I2S мікрофона");
        sd_card_deinit();
        return;
    }

    /* 4. Відкриття WAV файлу для запису (16 кГц, 16 біт PCM, 1 канал Mono) */
    wav_writer_t wav_writer;
    if (wav_writer_open(RECORD_FILE_PATH, mic_cfg.sample_rate, 16, 1, &wav_writer) != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося відкрити WAV-файл для запису");
        i2s_mic_deinit(&mic_dev);
        sd_card_deinit();
        return;
    }

    /* 5. Запуск захоплення аудіо з I2S */
    if (i2s_mic_start(&mic_dev) != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося запустити захоплення I2S");
        wav_writer_close(&wav_writer);
        i2s_mic_deinit(&mic_dev);
        sd_card_deinit();
        return;
    }

    /* Розрахунок необхідного обсягу семплів для заданої тривалості */
    uint32_t total_target_samples = mic_cfg.sample_rate * RECORD_DURATION_SEC;
    uint32_t samples_processed = 0;

    /* Проміжний буфер для збереження 16-бітних PCM семплів */
    int16_t pcm16_buffer[I2S_MIC_DEFAULT_DMA_FRAME_NUM];

    ESP_LOGI(TAG, "Початок запису аудіо тривалістю %d сек... Говоріть у мікрофон!", RECORD_DURATION_SEC);

    /* 6. Фоновий цикл читання з DMA/подвійного буфера та потокового запису у файл */
    while (samples_processed < total_target_samples) {
        int32_t *raw_buf = NULL;
        size_t samples_read = 0;

        /* Безблокуюче/з таймаутом отримання готового буфера I2S DMA */
        esp_err_t err = i2s_mic_get_buffer(&mic_dev, &raw_buf, &samples_read, pdMS_TO_TICKS(100));
        if (err == ESP_OK && samples_read > 0) {
            /* Конвертація 24-бітних MSB-вирівняних даних у 16-біт PCM */
            size_t converted = i2s_mic_convert_32to16(raw_buf, pcm16_buffer, samples_read);

            /* Запис 16-бітних PCM семплів у WAV-файл */
            err = wav_writer_write(&wav_writer, pcm16_buffer, converted * sizeof(int16_t));
            if (err != ESP_OK) {
                ESP_LOGE(TAG, "Помилка запису в WAV-файл на SD-картці");
                break;
            }

            samples_processed += converted;
            i2s_mic_release_buffer(&mic_dev);
        } else if (err != ESP_ERR_TIMEOUT) {
            ESP_LOGW(TAG, "Попередження під час читання I2S буфера: %s", esp_err_to_name(err));
        }
    }

    ESP_LOGI(TAG, "Запис завершено. Оброблено %lu семплів.", (unsigned long)samples_processed);

    /* 7. Зупинка мікрофона, фіналізація WAV-заголовка та розмонтування SD-картки */
    i2s_mic_stop(&mic_dev);
    wav_writer_close(&wav_writer);
    i2s_mic_deinit(&mic_dev);
    sd_card_deinit();

    ESP_LOGI(TAG, "=== Програму завершено успішно. Аудіо збережено у %s ===", RECORD_FILE_PATH);
}

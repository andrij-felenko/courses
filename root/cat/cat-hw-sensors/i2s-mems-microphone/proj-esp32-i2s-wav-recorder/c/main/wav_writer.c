/**
 * @file wav_writer.c
 * @brief Реалізація процедур формування та збереження WAV-файлу на SD-картку.
 */

#include "wav_writer.h"
#include <string.h>
#include "esp_log.h"

static const char *TAG = "WAV_WRITER";

esp_err_t wav_writer_open(const char *filepath, uint32_t sample_rate, uint16_t bits_per_sample, uint16_t num_channels, wav_writer_t *writer)
{
    if (filepath == NULL || writer == NULL) {
        ESP_LOGE(TAG, "Помилка: недійсні аргументи wav_writer_open");
        return ESP_ERR_INVALID_ARG;
    }

    memset(writer, 0, sizeof(wav_writer_t));

    writer->fp = fopen(filepath, "wb");
    if (writer->fp == NULL) {
        ESP_LOGE(TAG, "Не вдалося відкрити файл для запису: %s", filepath);
        return ESP_FAIL;
    }

    /* Заповнення полів заголовка RIFF/WAV */
    memcpy(writer->header.chunk_id, "RIFF", 4);
    writer->header.chunk_size = 36; /* Початковий розмір заголовка без даних */
    memcpy(writer->header.format, "WAVE", 4);

    memcpy(writer->header.subchunk1_id, "fmt ", 4);
    writer->header.subchunk1_size = 16; /* PCM */
    writer->header.audio_format = 1;     /* Нестиснений PCM */
    writer->header.num_channels = num_channels;
    writer->header.sample_rate = sample_rate;
    writer->header.bits_per_sample = bits_per_sample;
    writer->header.byte_rate = sample_rate * num_channels * (bits_per_sample / 8);
    writer->header.block_align = num_channels * (bits_per_sample / 8);

    memcpy(writer->header.subchunk2_id, "data", 4);
    writer->header.subchunk2_size = 0; /* Буде оновлено після завершення запису */

    /* Запис тимчасового заголовка на початок файлу */
    size_t written = fwrite(&writer->header, sizeof(wav_header_t), 1, writer->fp);
    if (written != 1) {
        ESP_LOGE(TAG, "Помилка запису заголовка WAV у файл");
        fclose(writer->fp);
        writer->fp = NULL;
        return ESP_FAIL;
    }

    writer->bytes_written = 0;
    writer->is_open = true;

    ESP_LOGI(TAG, "Створено WAV файл '%s' (%lu Гц, %u біт, %u кан.)",
             filepath, (unsigned long)sample_rate, bits_per_sample, num_channels);

    return ESP_OK;
}

esp_err_t wav_writer_write(wav_writer_t *writer, const void *data, size_t size)
{
    if (writer == NULL || data == NULL || !writer->is_open || writer->fp == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (size == 0) {
        return ESP_OK;
    }

    size_t bytes_written = fwrite(data, 1, size, writer->fp);
    if (bytes_written != size) {
        ESP_LOGE(TAG, "Помилка запису блоку даних у WAV файл: записано %zu з %zu", bytes_written, size);
        return ESP_FAIL;
    }

    writer->bytes_written += bytes_written;
    return ESP_OK;
}

esp_err_t wav_writer_finalize(wav_writer_t *writer)
{
    if (writer == NULL || !writer->is_open || writer->fp == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    /* Оновлення розмірів у заголовку */
    writer->header.subchunk2_size = writer->bytes_written;
    writer->header.chunk_size = 36 + writer->bytes_written;

    /* Переміщення покажчика у початок файлу для оновлення заголовка */
    if (fseek(writer->fp, 0, SEEK_SET) != 0) {
        ESP_LOGE(TAG, "Помилка fseek при підготовці оновлення заголовка WAV");
        return ESP_FAIL;
    }

    size_t written = fwrite(&writer->header, sizeof(wav_header_t), 1, writer->fp);
    if (written != 1) {
        ESP_LOGE(TAG, "Помилка перезапису заголовка WAV");
        return ESP_FAIL;
    }

    fflush(writer->fp);
    ESP_LOGI(TAG, "Заголовок WAV оновлено: ChunkSize=%lu, Subchunk2Size=%lu",
             (unsigned long)writer->header.chunk_size, (unsigned long)writer->header.subchunk2_size);

    return ESP_OK;
}

esp_err_t wav_writer_close(wav_writer_t *writer)
{
    if (writer == NULL || !writer->is_open) {
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t err = wav_writer_finalize(writer);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Фіналізація заголовка завершилася з помилкою %d", err);
    }

    if (writer->fp != NULL) {
        fclose(writer->fp);
        writer->fp = NULL;
    }

    writer->is_open = false;
    ESP_LOGI(TAG, "WAV-файл успішно закрито. Всього записано %lu байтів PCM даних", (unsigned long)writer->bytes_written);
    return ESP_OK;
}

/**
 * @file wav_writer.h
 * @brief Оголошення C-інтерфейсу формування файлу формату RIFF/WAV та запису PCM-потоку.
 */

#ifndef WAV_WRITER_H
#define WAV_WRITER_H

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Упакована структура заголовка WAV (44 байти) згідно зі специфікацією RIFF
 */
typedef struct __attribute__((packed)) {
    char     chunk_id[4];      /**< Ідентифікатор контейнера: "RIFF" */
    uint32_t chunk_size;      /**< Розмір файлу мінус 8 байтів (36 + subchunk2_size) */
    char     format[4];        /**< Формат: "WAVE" */
    char     subchunk1_id[4];  /**< Ідентифікатор підблоку формату: "fmt " */
    uint32_t subchunk1_size;  /**< Розмір підблоку формату (16 для нестисненого PCM) */
    uint16_t audio_format;    /**< Код формату аудіо (1 = PCM) */
    uint16_t num_channels;    /**< Кількість каналів (1 = Моно, 2 = Стерео) */
    uint32_t sample_rate;     /**< Частота дискретизації (Гц) */
    uint32_t byte_rate;       /**< Байт за секунду: SampleRate * NumChannels * BitsPerSample / 8 */
    uint16_t block_align;     /**< Вирівнювання блоку: NumChannels * BitsPerSample / 8 */
    uint16_t bits_per_sample; /**< Глибина оцифрування (8, 16, 24, 32 біт) */
    char     subchunk2_id[4];  /**< Ідентифікатор підблоку даних: "data" */
    uint32_t subchunk2_size;  /**< Розмір аудіоданих у байтах */
} wav_header_t;

/**
 * @brief Контекст для потокового запису WAV-файлу
 */
typedef struct {
    FILE *fp;                 /**< Файловий дескриптор VFS POSIX */
    wav_header_t header;      /**< Структура заголовка WAV */
    uint32_t bytes_written;   /**< Загальна кількість записаних байтів аудіоданих */
    bool is_open;             /**< Прапор відкритого файлу */
} wav_writer_t;

/**
 * @brief Створення нового WAV-файлу та запис початкового 44-байтного заголовка
 *
 * @param[in] filepath Повний шлях до файлу (наприклад, "/sdcard/rec.wav")
 * @param[in] sample_rate Частота дискретизації (наприклад, 16000 або 44100)
 * @param[in] bits_per_sample Кількість біт на семпл (16 або 32)
 * @param[in] num_channels Кількість каналів (1 = Моно, 2 = Стерео)
 * @param[out] writer Вказівник на структуру контексту запису WAV
 * @return ESP_OK у разі успішного створення файлу та заголовка
 */
esp_err_t wav_writer_open(const char *filepath, uint32_t sample_rate, uint16_t bits_per_sample, uint16_t num_channels, wav_writer_t *writer);

/**
 * @brief Запис блоку PCM-аудіоданих у файл
 *
 * @param[in] writer Вказівник на контекст WAV-записувача
 * @param[in] data Вказівник на буфер PCM-семплів
 * @param[in] size Розмір буфера у байтах
 * @return ESP_OK у разі успішного запису
 */
esp_err_t wav_writer_write(wav_writer_t *writer, const void *data, size_t size);

/**
 * @brief Оновлення полів розмірів ChunkSize та Subchunk2Size у заголовку WAV
 *
 * @param[in] writer Вказівник на контекст WAV-записувача
 * @return ESP_OK у разі успішного перезапису заголовка
 */
esp_err_t wav_writer_finalize(wav_writer_t *writer);

/**
 * @brief Фіналізація заголовка та закриття WAV-файлу
 *
 * @param[in] writer Вказівник на контекст WAV-записувача
 * @return ESP_OK у разі успішного закриття файлу
 */
esp_err_t wav_writer_close(wav_writer_t *writer);

#ifdef __cplusplus
}
#endif

#endif /* WAV_WRITER_H */

/**
 * @file i2s_mic.h
 * @brief Драйвер захоплення аудіо з MEMS-мікрофона INMP441 через I2S в ESP-IDF.
 */

#ifndef I2S_MIC_H
#define I2S_MIC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "driver/gpio.h"
#include "driver/i2s.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#ifdef __cplusplus
extern "C" {
#endif

/** Типові GPIO-піни для підключення INMP441 до ESP32 */
#define I2S_MIC_DEFAULT_SCK_PIN   GPIO_NUM_14  /**< Continuous Serial Clock (BCLK) */
#define I2S_MIC_DEFAULT_WS_PIN    GPIO_NUM_15  /**< Word Select / Left Right Clock (LRCK) */
#define I2S_MIC_DEFAULT_SD_PIN    GPIO_NUM_32  /**< Serial Data Out (SD) */

/** Типові параметри дискретизації аудіо */
#define I2S_MIC_DEFAULT_SAMPLE_RATE  16000     /**< Частота дискретизації 16 кГц */
#define I2S_MIC_DEFAULT_DMA_FRAME_NUM 512       /**< Кількість фреймів у DMA-буфері */
#define I2S_MIC_DEFAULT_DMA_DESC_NUM  6         /**< Кількість DMA-описників */

/** Кількість буферів у схемі подвійного буферизування (Ping-Pong) */
#define I2S_MIC_PINGPONG_BUFFERS     2

/**
 * @brief Конфігурація драйвера I2S-мікрофона
 */
typedef struct {
    i2s_port_t i2s_port;          /**< Порт I2S (наприклад, I2S_NUM_0) */
    gpio_num_t sck_pin;           /**< Пін SCK (BCLK) */
    gpio_num_t ws_pin;            /**< Пін WS (LRCK) */
    gpio_num_t sd_pin;            /**< Пін SD (Data In) */
    uint32_t sample_rate;         /**< Частота дискретизації (Гц) */
    size_t dma_frame_num;         /**< Кількість слів у одному DMA-буфері */
    size_t dma_desc_num;          /**< Загальна кількість DMA-описників */
} i2s_mic_config_t;

/**
 * @brief Структура підсистеми подвійного пінг-понг буфера
 */
typedef struct {
    int32_t *raw_buffers[I2S_MIC_PINGPONG_BUFFERS]; /**< Масив з 2 буферів у SRAM під 32-бітні PCM-семпли */
    size_t buffer_size_bytes;                       /**< Розмір одного буфера в байтах */
    size_t buffer_capacity_samples;                 /**< Місткість одного буфера в семплах */
    uint8_t write_index;                            /**< Індекс буфера, що зараз заповнюється I2S/DMA */
    uint8_t read_index;                             /**< Індекс буфера, готового для зчитування завданням */
    SemaphoreHandle_t ready_sem;                    /**< Семафор готовності заповненого буфера */
    SemaphoreHandle_t lock;                         /**< М'ютекс для потокобезпечного перемикання */
    bool is_running;                                /**< Прапор активності фонового зчитування */
} i2s_mic_dev_t;

/**
 * @brief Ініціалізація драйвера I2S-мікрофона та подвійного буфера
 *
 * @param[in] config Вказівник на конфігурацію I2S та GPIO
 * @param[out] dev Вказівник на структуру пристрою
 * @return ESP_OK у разі успіху або відповідний код помилки esp_err_t
 */
esp_err_t i2s_mic_init(const i2s_mic_config_t *config, i2s_mic_dev_t *dev);

/**
 * @brief Запуск зчитування PCM-даних з мікрофона
 *
 * @param[in] dev Вказівник на структуру пристрою
 * @return ESP_OK у разі успіху
 */
esp_err_t i2s_mic_start(i2s_mic_dev_t *dev);

/**
 * @brief Отримання готового заповненого буфера PCM-даних (безблокуюче або з таймаутом)
 *
 * @param[in] dev Вказівник на структуру пристрою
 * @param[out] out_buffer Вказівник на отриманий буфер з 32-бітними PCM-семплами
 * @param[out] out_samples Кількість семплів у буфері
 * @param[in] wait_ticks Час очікування у тіках FreeRTOS
 * @return ESP_OK якщо буфер отримано, ESP_ERR_TIMEOUT якщо буфер не готовий
 */
esp_err_t i2s_mic_get_buffer(i2s_mic_dev_t *dev, int32_t **out_buffer, size_t *out_samples, TickType_t wait_ticks);

/**
 * @brief Звільнення обробленого буфера після читання
 *
 * @param[in] dev Вказівник на структуру пристрою
 * @return ESP_OK у разі успіху
 */
esp_err_t i2s_mic_release_buffer(i2s_mic_dev_t *dev);

/**
 * @brief Зупинка зчитування з I2S-мікрофона
 *
 * @param[in] dev Вказівник на структуру пристрою
 * @return ESP_OK у разі успіху
 */
esp_err_t i2s_mic_stop(i2s_mic_dev_t *dev);

/**
 * @brief Деініціалізація драйвера I2S та вивільнення ресурсів пам'яті
 *
 * @param[in] dev Вказівник на структуру пристрою
 * @return ESP_OK у разі успіху
 */
esp_err_t i2s_mic_deinit(i2s_mic_dev_t *dev);

/**
 * @brief Конвертація 24-бітних PCM-семплів INMP441 (у 32-бітному слоті) в 16-бітні PCM-семпли
 *
 * @param[in] src Вхідний масив 32-бітних слів від I2S DMA
 * @param[out] dst Вихідний масив 16-бітних знакових цілих (PCM 16-bit)
 * @param[in] num_samples Кількість семплів для конвертації
 * @return Кількість конвертованих семплів
 */
size_t i2s_mic_convert_32to16(const int32_t *src, int16_t *dst, size_t num_samples);

#ifdef __cplusplus
}
#endif

#endif /* I2S_MIC_H */

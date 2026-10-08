#ifndef OV2640_DRIVER_H
#define OV2640_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Перелічення підтримуваних роздільностей кадру.
 */
typedef enum {
    FRAMESIZE_CIF = 0,   /**< 352x288 */
    FRAMESIZE_SVGA,      /**< 800x600 */
    FRAMESIZE_UXGA,      /**< 1600x1200 */
} framesize_t;

/**
 * @brief Перелічення форматів пікселів вихідного потоку.
 */
typedef enum {
    PIXFORMAT_RGB565 = 0,
    PIXFORMAT_YUV422,
    PIXFORMAT_GRAYSCALE,
    PIXFORMAT_JPEG,
} pixformat_t;

/**
 * @brief Структура кадрового буфера в оперативній пам'яті PSRAM.
 */
typedef struct {
    uint8_t *buf;          /**< Вказівник на двійкові байти зображення у PSRAM */
    size_t len;            /**< Фактичний розмір кадру у байтах */
    size_t width;          /**< Ширина кадру у пікселях */
    size_t height;         /**< Висота кадру у пікселях */
    pixformat_t format;    /**< Формат даних (JPEG/YUV/RGB) */
    int64_t timestamp;     /**< Системна часова мітка захоплення кадру (мікросекунди) */
} camera_fb_t;

/**
 * @brief Структура конфігурації пинів DVP та параметрів роботи драйвера OV2640.
 */
typedef struct {
    int pin_pwdn;          /**< GPIO підключення Power Down (PWDN) (-1 якщо не використовується) */
    int pin_reset;         /**< GPIO підключення Hardware Reset (-1 якщо не використовується) */
    int pin_xclk;          /**< GPIO генерації базової тактової частоти XCLK */
    int pin_sscb_sda;      /**< GPIO шини SCCB SIOD / SDA */
    int pin_sscb_scl;      /**< GPIO шини SCCB SIOC / SCL */

    int pin_d7;            /**< GPIO лінії даних DVP D7 */
    int pin_d6;            /**< GPIO лінії даних DVP D6 */
    int pin_d5;            /**< GPIO лінії даних DVP D5 */
    int pin_d4;            /**< GPIO лінії даних DVP D4 */
    int pin_d3;            /**< GPIO лінії даних DVP D3 */
    int pin_d2;            /**< GPIO лінії даних DVP D2 */
    int pin_d1;            /**< GPIO лінії даних DVP D1 */
    int pin_d0;            /**< GPIO лінії даних DVP D0 */

    int pin_vsync;         /**< GPIO сигналу кадрової синхронізації VSYNC */
    int pin_href;          /**< GPIO сигналу рядкової синхронізації HREF */
    int pin_pclk;          /**< GPIO тактового сигналу пікселів PCLK */

    uint32_t xclk_freq_hz; /**< Частота XCLK (зазвичай 20000000 Гц) */
    pixformat_t pix_format;/**< Бажаний формат вихідних даних */
    framesize_t frame_size;/**< Бажана роздільність кадру */
    uint8_t jpeg_quality;  /**< Коефіцієнт стиснення JPEG (1..63, менше = краща якість) */
    size_t fb_count;       /**< Кількість кадрових буферів DMA в PSRAM (1 або 2) */
} ov2640_config_t;

/**
 * @brief Повна ініціалізація периферії XCLK, SCCB, перевірка PID/MID, налаштування DVP I2S DMA та PSRAM.
 *
 * @param config Вказівник на структуру конфігурації.
 * @return ESP_OK у разі успіху, код помилки у разі збою.
 */
esp_err_t ov2640_init(const ov2640_config_t *config);

/**
 * @brief Деініціалізація драйвера камери, вимкнення DMA, LEDC та звільнення пам'яті PSRAM.
 *
 * @return ESP_OK у разі успіху.
 */
esp_err_t ov2640_deinit(void);

/**
 * @brief Програмне та апаратне скидання внутрішніх регістрів OV2640.
 *
 * @return ESP_OK у разі успішного скидання.
 */
esp_err_t ov2640_reset(void);

/**
 * @brief Зчитування системних ідентифікаційних регістрів PID (0x26) та VER (0x42).
 *
 * @param pid_mid Вказівник для збереження 16-бітного ідентифікатора (0x2640).
 * @return ESP_OK якщо пристрій відповідає очікуваному ідентифікатору.
 */
esp_err_t ov2640_check_id(uint16_t *pid_mid);

/**
 * @brief Отримання готового кадрового буфера з черги DMA PSRAM з очікуванням по таймауту.
 *
 * @param timeout_ms Час очікування кадру в мілісекундах.
 * @return Вказівник на структуру camera_fb_t або NULL у разі таймауту/помилки.
 */
camera_fb_t* ov2640_get_frame(uint32_t timeout_ms);

/**
 * @brief Повернення кадрового буфера назад у кільцевий буфер DMA після завершення обробки.
 *
 * @param fb Вказівник на кадр, отриманий з ov2640_get_frame().
 */
void ov2640_return_frame(camera_fb_t *fb);

/**
 * @brief Динамічна зміна роздільності кадру OV2640.
 *
 * @param size Нове значення роздільності (FRAMESIZE_CIF, FRAMESIZE_SVGA, FRAMESIZE_UXGA).
 * @return ESP_OK у разі успішної переконфігурації DSP.
 */
esp_err_t ov2640_set_framesize(framesize_t size);

/**
 * @brief Динамічна зміна якості компресії JPEG.
 *
 * @param quality Коефіцієнт стиснення (1..63).
 * @return ESP_OK у разі успішного запису в регістр QS.
 */
esp_err_t ov2640_set_quality(uint8_t quality);

#ifdef __cplusplus
}
#endif

#endif /* OV2640_DRIVER_H */

#ifndef DCMI_DMA_H
#define DCMI_DMA_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file dcmi_dma.h
 * @brief Оголошення апаратного інтерфейсу DCMI та розширеного контролера DMA у режимі Double Buffer Mode.
 *
 * Модуль забезпечує захоплення відеопотоку з сенсора OV3640, узгодження сигналів синхронізації
 * (HSYNC, VSYNC, PIXCLK), обробку переривань кадру/рядка/переповнення та потокове виявлення
 * маркерів JPEG (SOI 0xFFD8, EOI 0xFFD9) без блокування ядра процесора.
 */

/* Бінарні маркери потоку JPEG */
#define JPEG_MARKER_PREFIX   0xFF
#define JPEG_MARKER_SOI      0xD8
#define JPEG_MARKER_EOI      0xD9

/**
 * @brief Коди помилок та результати виконання функцій DCMI/DMA.
 */
typedef enum {
    DCMI_DMA_OK = 0,             /**< Успішне виконання */
    DCMI_DMA_ERR_PARAM = -1,     /**< Некоректні аргументи */
    DCMI_DMA_ERR_BUSY = -2,      /**< Модуль уже працює */
    DCMI_DMA_ERR_OVERRUN = -3,   /**< Переповнення буфера даних (Overrun) */
    DCMI_DMA_ERR_NO_MEM = -4     /**< Недостатньо пам'яті для розміщення буферів */
} dcmi_dma_status_t;

/**
 * @brief Активний DMA-буфер подвійного кільцевого режиму.
 */
typedef enum {
    DCMI_DMA_BUF_0 = 0,
    DCMI_DMA_BUF_1 = 1
} dcmi_dma_buf_index_t;

/**
 * @brief Стан кадрового автомата DCMI.
 */
typedef enum {
    FRAME_STATE_IDLE = 0,        /**< Простій, захоплення вимкнено */
    FRAME_STATE_CAPTURING,       /**< Триває активне приймання потоку пікселів */
    FRAME_STATE_READY,           /**< Кадр повністю прийнято й перевірено */
    FRAME_STATE_OVERRUN,         /**< Фіксація апаратного переповнення DMA/DCMI */
    FRAME_STATE_ERROR            /**< Помилка з синхронізацією */
} dcmi_frame_state_t;

/**
 * @brief Полярність апаратних сигналів синхронізації DCMI.
 */
typedef struct {
    uint8_t pclk_polarity;  /**< 0 — спадаючий фронт, 1 — наростаючий фронт PIXCLK */
    uint8_t hsync_polarity; /**< 0 — активний низький, 1 — активний високий HSYNC */
    uint8_t vsync_polarity; /**< 0 — активний низький, 1 — активний високий VSYNC */
    bool byte_swap;         /**< Перестановка байтів у 32-бітному слові DMA */
} dcmi_hw_config_t;

/**
 * @brief Конструкція подвійного буфера DMA (Double Buffer Mode).
 */
typedef struct {
    uint32_t *buf0;               /**< Вказівник на перший DMA буфер в RAM */
    uint32_t *buf1;               /**< Вказівник на другий DMA буфер в RAM */
    size_t buf_size_words;        /**< Розмір кожного буфера в 32-бітних словах */
    volatile uint32_t active_buf; /**< Індекс поточного буфера, куди пише DMA */
} dcmi_dma_double_buf_t;

/**
 * @brief Контекст неблокуючого аналізатора стиснутого потоку JPEG.
 */
typedef struct {
    uint8_t *jpeg_out_buf;     /**< Буфер призначення для зібраного JPEG кадру */
    size_t jpeg_max_size;      /**< Максимальна місткість вихідного буфера */
    size_t jpeg_actual_size;   /**< Обчислений розмір виділеного JPEG кадру у байтах */
    bool is_soi_found;         /**< Прапорець знаходження початку кадру (0xFFD8) */
    bool is_eoi_found;         /**< Прапорець знаходження кінця кадру (0xFFD9) */
    uint8_t last_byte;         /**< Останній оброблений байт для перехідних маркерів */
} jpeg_parser_ctx_t;

/**
 * @brief Головний дескриптор контролера DCMI та DMA.
 */
typedef struct {
    dcmi_hw_config_t hw_config;
    dcmi_dma_double_buf_t double_buf;
    jpeg_parser_ctx_t jpeg_parser;
    volatile dcmi_frame_state_t state;
    volatile uint32_t frame_count;
    volatile uint32_t line_count;
    volatile uint32_t overrun_count;
    bool is_jpeg_mode;

    /* Зворотні виклики (Callback) для сповіщення застосунку */
    void (*frame_complete_cb)(const uint8_t *frame_data, size_t length, bool is_jpeg);
    void (*error_cb)(dcmi_dma_status_t status);
} dcmi_dma_handle_t;

/* --- Прототипи функцій керування DCMI/DMA --- */

/**
 * @brief Конфігурування модулів DCMI й DMA, прив'язка подвійного буфера.
 * @param handle Вказівник на дескриптор DCMI/DMA.
 * @param buf0 Адреса першого кільцевого буфера.
 * @param buf1 Адреса другого кільцевого буфера.
 * @param buf_size_words Розмір одного буфера у 32-бітних словах.
 * @return DCMI_DMA_OK у разі успішної конфігурації.
 */
dcmi_dma_status_t dcmi_dma_init(dcmi_dma_handle_t *handle, uint32_t *buf0, uint32_t *buf1, size_t buf_size_words);

/**
 * @brief Запуск потокового апаратного захоплення кадрів через DMA.
 * @param handle Вказівник на дескриптор DCMI/DMA.
 * @return DCMI_DMA_OK.
 */
dcmi_dma_status_t dcmi_dma_start(dcmi_dma_handle_t *handle);

/**
 * @brief Зупинка апаратного захоплення DCMI.
 * @param handle Вказівник на дескриптор DCMI/DMA.
 * @return DCMI_DMA_OK.
 */
dcmi_dma_status_t dcmi_dma_stop(dcmi_dma_handle_t *handle);

/**
 * @brief Налаштування буфера призначення для збереження виділеного JPEG кадру.
 * @param handle Вказівник на дескриптор.
 * @param out_buf Буфер у пам'яті.
 * @param max_size Розмір буфера у байтах.
 */
void dcmi_dma_set_jpeg_buffer(dcmi_dma_handle_t *handle, uint8_t *out_buf, size_t max_size);

/**
 * @brief Обробник переривання периферії DCMI (FRAME, LINE, OVR events).
 * @param handle Вказівник на дескриптор DCMI/DMA.
 */
void dcmi_dma_irq_handler_dcmi(dcmi_dma_handle_t *handle);

/**
 * @brief Обробник переривання DMA в режимі подвійного буферизування (Double Buffer Transfer Complete).
 * @param handle Вказівник на дескриптор DCMI/DMA.
 */
void dcmi_dma_irq_handler_dma(dcmi_dma_handle_t *handle);

/**
 * @brief Потоковий неблокуючий аналіз блоку даних для пошуку маркерів SOI (0xFFD8) та EOI (0xFFD9).
 * @param handle Вказівник на дескриптор.
 * @param chunk Масив байтів із поточного DMA буфера.
 * @param chunk_size Кількість байтів у блоці.
 * @return true, якщо виділення цілісного JPEG кадру завершено.
 */
bool dcmi_dma_process_jpeg_chunk(dcmi_dma_handle_t *handle, const uint8_t *chunk, size_t chunk_size);

/**
 * @brief Скидання стану потокового парсера JPEG для нового кадру.
 * @param handle Вказівник на дескриптор.
 */
void dcmi_dma_reset_jpeg_parser(dcmi_dma_handle_t *handle);

#endif /* DCMI_DMA_H */

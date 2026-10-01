#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "esp_async_memcpy.h"

// Ширина та висота кадру для прикладу (320x240, 16 біт на піксель - RGB565)
#define FB_WIDTH        320
#define FB_HEIGHT       240
#define FB_BYTES_PER_PIXEL 2
#define FB_SIZE_BYTES   (FB_WIDTH * FB_HEIGHT * FB_BYTES_PER_PIXEL)

// Контекстна структура подвійної буферизації у PSRAM
typedef struct {
    uint8_t *buffer_a;          // Перший кадровий масив у PSRAM
    uint8_t *buffer_b;          // Другий кадровий масив у PSRAM
    uint8_t *front_buffer;      // Буфер, що виводиться на екран (або передається через DMA)
    uint8_t *back_buffer;       // Буфер, у який малюється наступний кадр
    size_t size;                // Розмір одного буфера у байтах
    bool swap_pending;          // Прапор готовності нового кадру для перемикання
    async_memcpy_handle_t async_memcpy; // Хендл асинхронного DMA-передавача
} psram_fb_t;

/**
 * @brief Ініціалізація подвійного кадрового буфера у PSRAM та налаштування DMA.
 * 
 * @param fb Вказівник на контекстну структуру.
 * @param width Ширина кадру в пікселях.
 * @param height Висота кадру в пікселях.
 * @return esp_err_t ESP_OK у разі успіху.
 */
esp_err_t psram_fb_init(psram_fb_t *fb, uint16_t width, uint16_t height);

/**
 * @brief Очищення кешу для робочого буфера (back buffer) перед передачею.
 * 
 * @param fb Вказівник на контекстну структуру.
 * @return esp_err_t ESP_OK у разі успіху.
 */
esp_err_t psram_fb_flush_cache(psram_fb_t *fb);

/**
 * @brief Безпечне перемикання активного та робочого буферів (double buffering).
 * 
 * @param fb Вказівник на контекстну структуру.
 */
void psram_fb_swap(psram_fb_t *fb);

/**
 * @brief Звільнення ресурсів пам'яті PSRAM та драйвера DMA.
 * 
 * @param fb Вказівник на контекстну структуру.
 */
void psram_fb_deinit(psram_fb_t *fb);
